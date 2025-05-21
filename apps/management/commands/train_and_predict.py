from django.core.management.base import BaseCommand
from apps.models import AQILog
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import pandas as pd
import numpy as np
import joblib
import os

class Command(BaseCommand):
    help = 'Latih model dan evaluasi prediksi AQI untuk 3 hari ke depan'

    def handle(self, *args, **kwargs):
        df = pd.DataFrame.from_records(AQILog.objects.all().values()) #mengambil dari dari db model AQIlog + dikonversi queryset django -> pandas dataframe
        df.sort_values("timestamp", inplace=True) #mengurutkan data berdasarkan timestamp secara ascending
        
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
        
        for col in numeric_cols:
            mean = df[col].mean()
            std = df[col].std()
            lower, upper = mean - 3*std, mean + 3*std
            outliers = df[(df[col] < lower) | (df[col] > upper)]

            print(f"[{col}] Jumlah outlier: {len(outliers)}")      
        
        
        # Fitur & target
        features = ['pm25', 'pm10', 'co', 'no2', 'so2', 'o3'] #variabel input yg digunakan u/ prediksi
        for lag in range(1, 4):
            df[f'aqi_t+{lag}'] = df['aqi'].shift(-lag)

        df.dropna(inplace=True) #menghapus NaN (hasil dari shifting)

        X = df[features] #variabel fitur
        y1, y2, y3 = df['aqi_t+1'], df['aqi_t+2'], df['aqi_t+3'] #variabel target

        X_train, X_test, y1_train, y1_test = train_test_split(X, y1, test_size=0.3, random_state=42)
        _, _, y2_train, y2_test = train_test_split(X, y2, test_size=0.3, random_state=42)
        _, _, y3_train, y3_test = train_test_split(X, y3, test_size=0.3, random_state=42)

        model1 = RandomForestRegressor().fit(X_train, y1_train)
        model2 = RandomForestRegressor().fit(X_train, y2_train)
        model3 = RandomForestRegressor().fit(X_train, y3_train)

        # Simpan model
        os.makedirs("models", exist_ok=True)
        joblib.dump(model1, "models/rf_day1.pkl")
        joblib.dump(model2, "models/rf_day2.pkl")
        joblib.dump(model3, "models/rf_day3.pkl")

        # Evaluasi
        def evaluate(model, X_test, y_test, label):
            y_pred = model.predict(X_test)
            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            r2 = r2_score(y_test, y_pred)
            self.stdout.write(self.style.NOTICE(f"\n[{label}] Evaluasi Model:"))
            self.stdout.write(f"MAE: {mae:.2f}")
            self.stdout.write(f"RMSE: {rmse:.2f}")
            self.stdout.write(f"R²: {r2:.2f}")

        evaluate(model1, X_test, y1_test, "Besok")
        evaluate(model2, X_test, y2_test, "Lusa")
        evaluate(model3, X_test, y3_test, "3 Hari Lagi")

        # Prediksi terakhir
        last_data = X.iloc[[-1]] #ngambil data terbaru (baris terakhir)
        pred1 = model1.predict(last_data)[0]
        pred2 = model2.predict(last_data)[0]
        pred3 = model3.predict(last_data)[0]

        self.stdout.write(self.style.SUCCESS("\n✅ Model dilatih & dievaluasi!"))
        self.stdout.write(self.style.SUCCESS(f"📅 Prediksi Besok: {pred1:.2f}"))
        self.stdout.write(f"📅 Prediksi Lusa: {pred2:.2f}")
        self.stdout.write(f"📅 Prediksi 3 Hari Lagi: {pred3:.2f}")
