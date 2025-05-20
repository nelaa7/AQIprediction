import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from datetime import datetime, timedelta

# ======== [1] Load Data dari CSV ========
df = pd.read_csv("aqi4.csv")  # Ganti sesuai nama file kamu

# Fitur yang digunakan
features = ['pm25', 'pm10', 'co', 'no2', 'so2', 'o3']

# Bersihkan data
df = df.dropna(subset=['aqi'])  # pastikan kolom target tidak kosong

# Isi nilai kosong dengan mean
for col in features:
    df[col] = df[col].fillna(df[col].mean())

# Tambahkan fitur waktu jika ada
if 'timestamp' in df.columns:
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['hour'] = df['timestamp'].dt.hour
    df['day'] = df['timestamp'].dt.dayofweek
else:
    df['hour'] = 12
    df['day'] = 2

# ======== [2] Model Regresi AQI ========
X = df[features + ['hour', 'day']]
y = df['aqi']

model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

# ======== [3] Evaluasi Model ========
y_pred = model.predict(X)

mae = mean_absolute_error(y, y_pred)
rmse = np.sqrt(mean_squared_error(y, y_pred))
r2 = r2_score(y, y_pred)

print("\n=== Evaluasi Model ===")
print(f"MAE:  {mae:.2f}")
print(f"RMSE: {rmse:.2f}")
print(f"R²:   {r2:.2f}")

# ======== [4] Prediksi 3 Hari ke Depan (setiap jam) ========
latest = df.iloc[-1]
base_feat = latest[features]

future_data = []
now = datetime.now()
for h in range(1, 3 * 24 + 1):
    t = now + timedelta(hours=h)
    row = base_feat.copy()
    row['hour'] = t.hour
    row['day'] = t.weekday()
    row['timestamp'] = t
    future_data.append(row)

future_df = pd.DataFrame(future_data)
future_df['predicted_aqi'] = model.predict(future_df[features + ['hour', 'day']])

# Tampilkan hasil prediksi
print("\n=== Prediksi AQI 3 Hari ke Depan ===")
for _, row in future_df.iterrows():
    ts = row['timestamp'].strftime("%Y-%m-%d %H:%M")
    aq = round(row['predicted_aqi'], 2)
    print(f"{ts}: AQI ≈ {aq}")

# Simpan ke CSV
future_df.to_csv("prediksi_aqi_3_hari.csv", index=False)
print("\n=> Hasil prediksi disimpan ke 'prediksi_aqi_3_hari.csv'")
