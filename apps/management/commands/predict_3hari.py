import pandas as pd
from datetime import timedelta
from django.utils import timezone
from django.core.management.base import BaseCommand
from sklearn.ensemble import RandomForestRegressor
from apps.models import AQILog, PredictedAQI


class Command(BaseCommand):
    help = 'Preprocessing dan prediksi AQI 3 hari ke depan setiap jam'

    def handle(self, *args, **kwargs):
        self.stdout.write("\n[1] Mengambil data dari database...")

        # Ambil data dari DB
        qs = AQILog.objects.all()
        df = pd.DataFrame(qs.values())

        if df.empty:
            self.stdout.write(self.style.ERROR("Data AQILog kosong."))
            return

        self.stdout.write(f"[1] Data awal: {len(df)} baris")
        self.stdout.write(f"Contoh data:\n{df.head(3)}\n")

        self.stdout.write("[2] Preprocessing data...")

        # Konversi timestamp
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        # Drop NA di target
        df = df.dropna(subset=['aqi'])
        self.stdout.write(f"[2] Setelah dropna target AQI: {len(df)} baris")

        # Isi nilai kosong pada fitur
        features = ['pm25', 'pm10', 'co', 'no2', 'so2', 'o3']
        for col in features:
            mean_val = df[col].mean()
            df[col] = df[col].fillna(mean_val)
            self.stdout.write(f"Filling missing {col} dengan mean = {mean_val:.2f}")

        # Fitur waktu
        df['hour'] = df['timestamp'].dt.hour
        df['day'] = df['timestamp'].dt.dayofweek

        self.stdout.write(f"[2] Contoh data setelah preprocessing:\n{df[features + ['hour', 'day', 'aqi']].head(3)}\n")

        # Split fitur dan target
        X = df[features + ['hour', 'day']]
        y = df['aqi']

        self.stdout.write("[3] Melatih model Random Forest...")
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X, y)

        # Ambil data terakhir sebagai referensi prediksi
        latest = df.iloc[-1]
        base_feat = latest[features]

        self.stdout.write("[4] Membuat data untuk 3 hari ke depan...")

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
        self.stdout.write(f"[4] Contoh data prediksi input:\n{future_df.head(3)}\n")

        self.stdout.write("[5] Melakukan prediksi AQI...")
        future_df['predicted_aqi'] = model.predict(future_df[features + ['hour', 'day']])

        self.stdout.write("\n[6] Hasil Prediksi AQI (3 Hari ke Depan):")
        for _, row in future_df.iterrows():
            ts = row['timestamp'].strftime("%Y-%m-%d %H:%M")
            aq = round(row['predicted_aqi'], 2)
            self.stdout.write(f"{ts}: AQI ≈ {aq}")
            
        self.stdout.write("[7] Menyimpan hasil prediksi ke database...")
        PredictedAQI.objects.all().delete()  # opsional: kosongkan prediksi sebelumnya
        for _, row in future_df.iterrows():
            PredictedAQI.objects.create(
                timestamp=row['timestamp'],
                predicted_aqi=row['predicted_aqi']
            )
        self.stdout.write("✔️ Prediksi berhasil disimpan.")
