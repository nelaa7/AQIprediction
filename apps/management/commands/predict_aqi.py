import pandas as pd
from django.core.management.base import BaseCommand
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.model_selection import train_test_split
from apps.models import AQILog


class Command(BaseCommand):
    help = 'Preprocessing dan evaluasi model klasifikasi AQI'

    def handle(self, *args, **kwargs):
        self.stdout.write("[1] Mengambil data dari database...")

        qs = AQILog.objects.all()
        df = pd.DataFrame(qs.values())

        if df.empty:
            self.stdout.write(self.style.ERROR("Data AQILog kosong."))
            return

        self.stdout.write("[2] Preprocessing data...")

        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.dropna(subset=['aqi'])

        features = ['pm25', 'pm10', 'co', 'no2', 'so2', 'o3']
        for col in features:
            df[col] = df[col].fillna(df[col].mean())

        df['hour'] = df['timestamp'].dt.hour
        df['day'] = df['timestamp'].dt.dayofweek

        # Konversi AQI ke kategori
        def categorize_aqi(aqi):
            if aqi <= 50:
                return 'Baik'
            elif aqi <= 100:
                return 'Sedang'
            elif aqi <= 200:
                return 'Tidak Sehat'
            elif aqi <= 300:
                return 'Tidak Sehat'
            else:
                return 'Sangat Tidak Sehat'

        df['aqi_category'] = df['aqi'].apply(categorize_aqi)

        self.stdout.write("[3] Melatih model Random Forest Classifier...")

        X = df[features + ['hour', 'day']]
        y = df['aqi_category']

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        self.stdout.write("\n[4] Classification Report:")
        self.stdout.write(classification_report(y_test, y_pred))

        labels = sorted(y.unique())
        cm = confusion_matrix(y_test, y_pred, labels=labels)

        self.stdout.write("\n[5] Confusion Matrix:")
        self.stdout.write("Label: " + str(labels))
        for actual, row in zip(labels, cm):
            row_str = "  ".join(f"{val:4}" for val in row)
            self.stdout.write(f"{actual:<18} {row_str}")
