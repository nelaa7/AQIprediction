import matplotlib.pyplot as plt
import seaborn as sns
from django.core.management.base import BaseCommand
from apps.models import AQILog
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import pandas as pd
import numpy as np
import joblib
import os
from scipy.stats import zscore 

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
        
        
        # Visualisasi distribusi awal AQI
        plt.figure(figsize=(10, 5))
        sns.histplot(df['aqi'], bins=30, kde=True)
        plt.title('Distribusi Nilai AQI')
        plt.xlabel('AQI')
        plt.ylabel('Frekuensi')
        plt.savefig("models/aqi_distribution.png")
        plt.close()
        self.stdout.write(self.style.SUCCESS("📊 Distribusi AQI disimpan ke 'models/aqi_distribution.png'"))

        
        # Visualisasi outlier untuk masing-masing kolom
        for col in numeric_cols:
            # Hitung Z-score
            z_scores = zscore(df[col])
            outliers_z = np.where(np.abs(z_scores) > 3)[0]  # ambil index outlier

            # Logging jumlah outlier
            self.stdout.write(f" [{col}] Jumlah outlier {len(outliers_z)}")
            plt.figure(figsize=(8, 4))
            sns.boxplot(x=df[col])
            plt.title(f'Boxplot {col}')
            plt.savefig(f"models/boxplot_{col}.png")
            plt.close()
            self.stdout.write(f"📦 Boxplot kolom {col} disimpan ke 'models/boxplot_{col}.png'")
        
        # Fitur & target
        features = ['pm25', 'pm10', 'co', 'no2', 'so2', 'o3'] #variabel input yg digunakan u/ prediksi
        for lag in range(1, 4):
            df[f'aqi_t+{lag}'] = df['aqi'].shift(-lag)

        df.dropna(inplace=True) #menghapus NaN (hasil dari shifting)

        X = df[features] #variabel fitur
        y1, y2, y3 = df['aqi_t+1'], df['aqi_t+2'], df['aqi_t+3'] #variabel target

        X_train, X_test, y1_train, y1_test = train_test_split(X, y1, test_size=0.2, random_state=42)
        _, _, y2_train, y2_test = train_test_split(X, y2, test_size=0.2, random_state=42)
        _, _, y3_train, y3_test = train_test_split(X, y3, test_size=0.2, random_state=42)

        model1 = RandomForestRegressor().fit(X_train, y1_train)
        model2 = RandomForestRegressor().fit(X_train, y2_train)
        model3 = RandomForestRegressor().fit(X_train, y3_train)

        # Simpan model
        os.makedirs("models", exist_ok=True)
        joblib.dump(model1, "models/rf_day1.pkl")
        joblib.dump(model2, "models/rf_day2.pkl")
        joblib.dump(model3, "models/rf_day3.pkl")
        
        # Evaluasi model dan visualisasi prediksi vs aktual
        def evaluate(model, X_test, y_test, label):
            y_pred = model.predict(X_test)
            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            r2 = r2_score(y_test, y_pred)

            # Plot prediksi vs aktual
            plt.figure(figsize=(6, 6))
            plt.scatter(y_test, y_pred, alpha=0.5)
            plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--')
            plt.title(f'Prediksi vs Aktual - {label}')
            plt.xlabel('Aktual')
            plt.ylabel('Prediksi')
            plt.grid(True)
            plt.savefig(f"models/pred_vs_actual_{label}.png")
            plt.close()

            self.stdout.write(self.style.NOTICE(f"\n[{label}] Evaluasi Model:"))
            self.stdout.write(f"MAE: {mae:.2f}")
            self.stdout.write(f"RMSE: {rmse:.2f}")
            self.stdout.write(f"R²: {r2:.2f}")
            self.stdout.write(f"📈 Plot prediksi vs aktual disimpan ke 'models/pred_vs_actual_{label}.png'")
        
        
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

        
        # Visualisasi Feature Importance dari model 1 (besok)
        importances = model1.feature_importances_
        plt.figure(figsize=(8, 4))
        sns.barplot(x=features, y=importances)
        plt.title('Feature Importance (Model Hari Besok)')
        plt.xlabel('Fitur')
        plt.ylabel('Pentingnya')
        plt.savefig("models/feature_importance_day1.png")
        plt.close()
        self.stdout.write("🔥 Visualisasi feature importance disimpan ke 'models/feature_importance_day1.png'")
