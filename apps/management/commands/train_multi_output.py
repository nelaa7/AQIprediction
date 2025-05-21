from django.core.management.base import BaseCommand
from apps.models import AQILog
from sklearn.ensemble import RandomForestRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import pandas as pd
import numpy as np
import joblib
import os

class Command(BaseCommand):
    help = 'Latih 1 model multi-output untuk prediksi AQI 3 hari ke depan'

    def handle(self, *args, **kwargs):
        df = pd.DataFrame.from_records(AQILog.objects.all().values())
        df.sort_values("timestamp", inplace=True)
        
        numeric_cols = ['pm25', 'pm10', 'co', 'no2', 'so2', 'o3', 'aqi']
        total_missing_before = df[numeric_cols].isnull().sum().sum()
        self.stdout.write(self.style.WARNING(f"\nTotal missing value sebelum preprocessing: {total_missing_before}"))
        self.stdout.write(str(df[numeric_cols].isnull().sum()))
        
        numeric_cols = ['pm25', 'pm10', 'co', 'no2', 'so2', 'o3', 'aqi']
        for col in numeric_cols:
            mean_val = df[col].mean()
            df[col] = df[col].fillna(mean_val)
            
        total_missing_after = df[numeric_cols].isnull().sum()
        self.stdout.write((f"\nTotal missing value setelah : {total_missing_after}"))

        features = ['pm25', 'pm10', 'co', 'no2', 'so2', 'o3']

        # Buat target untuk besok, lusa, 3 hari lagi
        for lag in range(1, 4):
            df[f'aqi_t+{lag}'] = df['aqi'].shift(-lag)

        df.dropna(inplace=True)

        X = df[features]
        Y = df[['aqi_t+1', 'aqi_t+2', 'aqi_t+3']]

        X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

        model = MultiOutputRegressor(RandomForestRegressor())
        model.fit(X_train, Y_train)

        # Simpan model
        os.makedirs("models", exist_ok=True)
        joblib.dump(model, "models/rf_multi.pkl")

        # Evaluasi
        Y_pred = model.predict(X_test)

        self.stdout.write(self.style.NOTICE("\n Evaluasi Model Multi-Output:"))

        for i, label in enumerate(['Besok', 'Lusa', '3 Hari Lagi']):
            mae = mean_absolute_error(Y_test.iloc[:, i], Y_pred[:, i])
            rmse = np.sqrt(mean_squared_error(Y_test.iloc[:, i], Y_pred[:, i]))
            r2 = r2_score(Y_test.iloc[:, i], Y_pred[:, i])
            self.stdout.write(f"[{label}] MAE: {mae:.2f} | RMSE: {rmse:.2f} | R²: {r2:.2f}")

        # Prediksi berdasarkan data terbaru
        last_data = X.iloc[[-1]]
        preds = model.predict(last_data)[0]
        self.stdout.write(self.style.SUCCESS("\n Model multi-output berhasil dilatih"))
        self.stdout.write(f" Prediksi Besok: {preds[0]:.2f}")
        self.stdout.write(f" Prediksi Lusa: {preds[1]:.2f}")
        self.stdout.write(f" Prediksi 3 Hari Lagi: {preds[2]:.2f}")
