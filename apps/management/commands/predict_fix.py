import time
import pandas as pd
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.management.base import BaseCommand
import schedule
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from apps.models import AQILog, PredictedAQI
import numpy as np

class Command(BaseCommand):
    help = 'Evaluasi model klasifikasi + prediksi AQI 3 hari ke depan'

    def __init__(self):
        super().__init__()
        self.counter = 0

    def handle(self, *args, **kwargs):
        schedule.every(1).minutes.do(self.job)  # ganti ke 15 menit
        self.stdout.write(self.style.SUCCESS("Scheduler berjalan. Menunggu tiap 15 menit ..."))
        while True:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.stdout.write(f"[{now}] Menunggu proses prediksi ...")
            schedule.run_pending()
            time.sleep(1)

    def job(self):
        self.counter += 1
        self.stdout.write(self.style.WARNING(f"===> Melakukan prediksi ke-{self.counter}"))
        data = self.predict_aqi()
        if data:
            self.stdout.write(self.style.SUCCESS(f"Data berhasil disimpan: {data}"))
        else:
            self.stdout.write(self.style.ERROR("Gagal ambil data"))

    def predict_aqi(self):
        try:
            self.stdout.write("[1] Mengambil data dari database...")
            qs = AQILog.objects.all()
            df = pd.DataFrame(qs.values())

            if df.empty:
                self.stdout.write(self.style.ERROR("Data AQILog kosong."))
                return

            self.stdout.write(f"[1] Data awal: {len(df)} baris")
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.dropna(subset=['aqi'])

            features = ['pm25', 'pm10', 'co', 'no2', 'so2', 'o3']
            self.stdout.write("\n[INFO] Jumlah missing value:")
            self.stdout.write(str(df[features].isnull().sum()))
            for col in features:
                mean_val = df[col].mean()
                df[col] = df[col].fillna(mean_val)

            df['hour'] = df['timestamp'].dt.hour
            df['day'] = df['timestamp'].dt.dayofweek

            self.stdout.write("\n[INFO] Jumlah missing value setelah diganti nilai mean:")
            self.stdout.write(str(df[features].isnull().sum()))

            # === [2] Klasifikasi AQI === #
            self.stdout.write("\n=== [2] Klasifikasi Kualitas Udara ===")

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

            df['aqi_category'] = df['aqi'].apply(category_aqi)

            self.stdout.write("\n[INFO] Distribusi Label AQI:")
            self.stdout.write(str(df['aqi_category'].value_counts()))

            X_cls = df[features + ['hour', 'day']]
            y_cls = df['aqi_category']

            X_train, X_test, y_train, y_test = train_test_split(
                X_cls, y_cls, test_size=0.2, random_state=42, stratify=y_cls
            )

            cls_model = RandomForestClassifier(n_estimators=10, random_state=42)
            cls_model.fit(X_train, y_train)
            y_pred = cls_model.predict(X_test)

            self.stdout.write("\n[2.1] Classification Report:")
            self.stdout.write(classification_report(y_test, y_pred))

            labels = sorted(y_cls.unique())
            cm = confusion_matrix(y_test, y_pred, labels=labels)

            self.stdout.write("\n[2.2] Confusion Matrix:")
            header = "Actual \\ Pred".ljust(22) + "".join([f"{label:<22}" for label in labels])
            self.stdout.write(header)
            for actual_label, row in zip(labels, cm):
                row_str = "".join([f"{val:<22}" for val in row])
                self.stdout.write(f"{actual_label:<22}{row_str}")

            # === [3] Prediksi AQI Regresi === #
            self.stdout.write("\n=== [3] Prediksi AQI 3 Hari ke Depan ===")

            X_reg = df[features + ['hour', 'day']]
            y_reg = df['aqi']

            reg_model = RandomForestRegressor(n_estimators=100, random_state=42)
            reg_model.fit(X_reg, y_reg)

            y_pred_reg = reg_model.predict(X_reg)
            mae = mean_absolute_error(y_reg, y_pred_reg)
            rmse = np.sqrt(mean_squared_error(y_reg, y_pred_reg))
            r2 = r2_score(y_reg, y_pred_reg)

            self.stdout.write("\n[3.1] Evaluasi Model Regresi:")
            self.stdout.write(f"MAE: {mae:.2f}")
            self.stdout.write(f"RMSE: {rmse:.2f}")
            self.stdout.write(f"R² Score: {r2:.2f}")

            latest = df.iloc[-1]
            base_feat = latest[features]

            future_data = []
            now = timezone.now()
            for h in range(1, 3 * 24 + 1):
                t = now + timedelta(hours=h)
                row = base_feat.copy()
                row['hour'] = t.hour
                row['day'] = t.weekday()
                row['timestamp'] = t
                future_data.append(row)

            future_df = pd.DataFrame(future_data)
            future_df['predicted_aqi'] = reg_model.predict(future_df[features + ['hour', 'day']])

            self.stdout.write("\n[3.2] Hasil Prediksi 3 Hari:")
            for _, row in future_df.iterrows():
                ts = row['timestamp'].strftime("%Y-%m-%d %H:%M")
                aq = round(row['predicted_aqi'], 2)
                self.stdout.write(f"{ts}: AQI ≈ {aq}")

            self.stdout.write("\n[3.3] Menyimpan ke database PredictedAQI...")
            PredictedAQI.objects.all().delete()
            for _, row in future_df.iterrows():
                PredictedAQI.objects.create(
                    timestamp=row['timestamp'],
                    predicted_aqi=row['predicted_aqi']
                )

            self.stdout.write("✔️ Semua selesai.")
            return True

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))
            return None
