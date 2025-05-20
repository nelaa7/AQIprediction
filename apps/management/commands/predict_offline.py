import pandas as pd
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split


class Command(BaseCommand):
    help = 'Prediksi AQI dan klasifikasi dari file CSV offline, hanya kolom dominan,aqi,pm25,pm10,co,no2,so2,o3'

    def handle(self, *args, **kwargs):
        try:
            # === [1] Baca data ===
            self.stdout.write("[1] Membaca data dari 'aqijkt.csv' ...")
            df = pd.read_csv("aqi_jkt.csv")

            # Validasi kolom
            expected_columns = ['parameter_pencemar_kritis', 'max', 'pm25', 'pm10', 'co', 'no2', 'so2', 'o3']
            missing_cols = set(expected_columns) - set(df.columns)
            if missing_cols:
                self.stdout.write(self.style.ERROR(f"❌ Kolom hilang: {missing_cols}"))
                return

            # Parsing waktu
            # df['timestamp'] = pd.to_datetime(df['log_date'], format='mixed', errors='coerce')
            # df.dropna(subset=['timestamp', 'max'], inplace=True)

            # === [2] Hapus duplikat ===
            self.stdout.write(f"[2] Jumlah data sebelum hapus duplikat: {len(df)}")
            df.drop_duplicates(inplace=True)
            self.stdout.write(f"[2] Setelah hapus duplikat: {len(df)}")

            # === [3] Handle missing values ===
            features = ['pm25', 'pm10', 'co', 'no2', 'so2', 'o3', 'max']
            for col in features:
                if df[col].isnull().sum() > 0:
                    mean_val = df[col].mean()
                    df[col] = df[col].fillna(mean_val)

            # === [4] Encode kolom 'dominan' ===
            df['parameter_pencemar_kritis'] = df['parameter_pencemar_kritis'].astype(str)
            df['dominan_code'] = df['parameter_pencemar_kritis'].astype('category').cat.codes
            features.insert(0, 'dominan_code')  # masukkan di awal fitur

            # === [5] Hapus outlier (IQR) ===
            def remove_outliers_iqr(data, column):
                Q1 = data[column].quantile(0.25)
                Q3 = data[column].quantile(0.75)
                IQR = Q3 - Q1
                lower = Q1 - 1.5 * IQR
                upper = Q3 + 1.5 * IQR
                return data[(data[column] >= lower) & (data[column] <= upper)]

            before = len(df)
            for col in features:
                df = remove_outliers_iqr(df, col)
            self.stdout.write(f"[5] Hapus outlier: dari {before} → {len(df)} baris")

            # === [6] Feature engineering ===
            # df['hour'] = df['timestamp'].dt.hour
            # df['day'] = df['timestamp'].dt.dayofweek

            # === [7] Klasifikasi AQI ===
            self.stdout.write("\n[7] Klasifikasi Kualitas Udara")

            def category_aqi(aqi):
                if aqi <= 50:
                    return 'Baik'
                elif aqi <= 100:
                    return 'Sedang'
                elif aqi <= 200:
                    return 'Tidak Sehat'
                elif aqi <= 300:
                    return 'Sangat Tidak Sehat'
                else:
                    return 'Berbahaya'

            df['aqi_category'] = df['max'].apply(category_aqi)

            X_cls = df[features]  # exclude 'aqi'
            y_cls = df['aqi_category']

            X_train, X_test, y_train, y_test = train_test_split(
                X_cls, y_cls, test_size=0.3, random_state=42, stratify=y_cls
            )

            cls_model = RandomForestClassifier(n_estimators=100, random_state=42)
            cls_model.fit(X_train, y_train)
            y_pred = cls_model.predict(X_test)

            self.stdout.write("\n[7.1] Classification Report:")
            self.stdout.write(classification_report(y_test, y_pred))

            labels = sorted(y_cls.unique())
            cm = confusion_matrix(y_test, y_pred, labels=labels)
            self.stdout.write("\n[7.2] Confusion Matrix:")
            for actual, row in zip(labels, cm):
                row_str = "  ".join(f"{val:4}" for val in row)
                self.stdout.write(f"{actual:<18} {row_str}")

            # === [8] Prediksi AQI Regresi ===
            self.stdout.write("\n[8] Prediksi AQI 3 Hari ke Depan")

            X_reg = df[features]
            y_reg = df['max']
            reg_model = RandomForestRegressor(n_estimators=100, random_state=42)
            reg_model.fit(X_reg, y_reg)

            latest = df.iloc[-1][features[:-1]]
            now = datetime.now()
            future_data = []

            for h in range(1, 3 * 24 + 1):
                t = now + timedelta(hours=h)
                row = latest.copy()
                row['hour'] = t.hour
                row['day'] = t.weekday()
                row['timestamp'] = t
                future_data.append(row)

            future_df = pd.DataFrame(future_data)
            future_df['predicted_aqi'] = reg_model.predict(future_df[features[:-1] + ['hour', 'day']])

            self.stdout.write("\n[8.1] Hasil Prediksi:")
            for _, row in future_df.iterrows():
                ts = row['timestamp'].strftime('%Y-%m-%d %H:%M')
                aqi = round(row['predicted_aqi'], 2)
                self.stdout.write(f"{ts} → AQI ≈ {aqi}")

            self.stdout.write("\n✔️ Selesai.")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"[ERROR] {e}"))
