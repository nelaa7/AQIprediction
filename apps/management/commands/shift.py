import pandas as pd
import matplotlib.pyplot as plt
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Latih model dan evaluasi prediksi AQI untuk 3 hari ke depan'

    def handle(self, *args, **kwargs):
# Data awal
        data = {
            'pm25': [60, 41, 51, 32, 37],
            'pm10': [0, 0, 0, 0, 0],
            'co': [51, 68, 65, 58, 58],
            'no2': [42, 53, 53, 43, 46],
            'so2': [50, 52, 69, 9, 64],
            'o3': [151, 98, 0, 82, 92],
            'aqi': [151, 98, 0, 82, 92]
        }
        df = pd.DataFrame(data)

        # Membuat kolom shifted
        for lag in range(1, 4):
            df[f'aqi_t+{lag}'] = df['aqi'].shift(-lag)

        # Drop baris dengan NaN (karena shift negatif)
        df.dropna(inplace=True)

        # Visualisasi
        plt.figure(figsize=(10,6))
        plt.plot(df.index, df['aqi'], marker='o', label='aqi (t)')
        plt.plot(df.index, df['aqi_t+1'], marker='o', label='aqi_t+1')
        plt.plot(df.index, df['aqi_t+2'], marker='o', label='aqi_t+2')
        plt.plot(df.index, df['aqi_t+3'], marker='o', label='aqi_t+3')

        plt.title('Visualisasi shifting kolom AQI')
        plt.xlabel('Index Data')
        plt.ylabel('AQI')
        plt.legend()
        plt.grid(True)
        plt.show()
