import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from django.core.management.base import BaseCommand
from apps.models import aqi_data

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        data = aqi_data.objects.filter(is_cleaned=True).values()
        df = pd.DataFrame(data)

        if df.empty:
            self.stdout.write("Belum ada data yang siap diprediksi")
            return

        # Anggap 'timestamp' dan 'aqi' tersedia
        df = df.sort_values('timestamp')
        X = df.drop(columns=['aqi'])
        y = df['aqi']

        model = RandomForestRegressor()
        model.fit(X, y)

        # Simulasi prediksi 3 hari ke depan
        future_X = ...  # kamu buat sendiri berdasarkan logikamu
        prediksi = model.predict(future_X)

        # Simpan hasil prediksi ke model PrediksiAQI misalnya
        self.stdout.write("Prediksi berhasil dilakukan")
