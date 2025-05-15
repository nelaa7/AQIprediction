import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from django.core.management.base import BaseCommand

from apps.models import AQILog  # import model di luar fungsi agar lebih rapi

class Command(BaseCommand):
    help = 'Preprocessing data untuk model ML'

    def handle(self, *args, **kwargs):
        # Jalankan preprocessing saat command dipanggil
        X_train_scaled, X_test_scaled, y_train, y_test = self.preprocess_for_ml()
        
        self.stdout.write("Preprocessing selesai.")
        self.stdout.write(f"Jumlah data train: {len(X_train_scaled)}, test: {len(X_test_scaled)}")
        
        import pandas as pd

        df_train = pd.DataFrame(X_train_scaled, columns=[
            'pm25', 'pm10', 'co', 'no2', 'so2', 'o3', 'hour', 'day'
        ])

        df_train['aqi'] = y_train.values  # gabungkan dengan target

        self.stdout.write("\nContoh data hasil preprocessing:")
        self.stdout.write(df_train.head(20).to_string())

    def preprocess_for_ml(self, location=None, start_date=None, end_date=None):
        # Ambil data dari DB
        qs = AQILog.objects.all()
        if location:
            qs = qs.filter(location=location)
        if start_date:
            qs = qs.filter(timestamp__date__gte=start_date)
        if end_date:
            qs = qs.filter(timestamp__date__lte=end_date)

        df = pd.DataFrame(qs.values())

        # Ubah kolom timestamp ke datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        # Drop baris dengan nilai target (AQI) kosong
        df = df.dropna(subset=['aqi'])

        # Isi missing values pada fitur dengan rata-rata kolom
        features = ['pm25', 'pm10', 'co', 'no2', 'so2', 'o3']
        for col in features:
            if col in df.columns:
                df[col] = df[col].fillna(df[col].mean())

        # Buat fitur baru dari timestamp
        df['hour'] = df['timestamp'].dt.hour
        df['day'] = df['timestamp'].dt.dayofweek

        # Pisahkan fitur dan target
        X = df[features + ['hour', 'day']]
        y = df['aqi']

        # Split data train dan test
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # # Normalisasi fitur
        # scaler = StandardScaler()
        # X_train_scaled = scaler.fit_transform(X_train)
        # X_test_scaled = scaler.transform(X_test)

        return X_train, X_test, y_train, y_test
