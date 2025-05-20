import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from datetime import datetime, timedelta

# ======== [1] Load Data dari CSV ========
df = pd.read_csv("aqi_jkt.csv")  # Ganti dengan nama file csv kamu

# Fitur input
features = ['pm25', 'pm10', 'co', 'no2', 'so2', 'o3']

# Target output: pakai kolom 'max' sebagai nilai AQI yang diprediksi
df = df.dropna(subset=['max'])  # pastikan target tidak kosong

# Isi nilai kosong pada fitur dengan rata-rata
for col in features:
    df[col] = df[col].fillna(df[col].mean())

# Buat kolom tanggal lengkap dari periode_data, bulan, tanggal
# Contoh: buat kolom 'date' dengan format yyyy-mm-dd
df['date'] = pd.to_datetime(df['periode_data'].astype(str) + '-' + df['bulan'].astype(str) + '-' + df['tanggal'].astype(str), errors='coerce')

# Buat fitur waktu
df['hour'] = 12  # karena tidak ada jam, kita set jam default 12 siang
df['day'] = df['date'].dt.dayofweek  # hari dalam minggu (0=Senin)

# ======== [2] Model Regresi AQI ========
X = df[features + ['hour', 'day']]
y = df['max']

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
    future_data.append(row)

future_df = pd.DataFrame(future_data)
future_df['predicted_aqi'] = model.predict(future_df[features + ['hour', 'day']])

# Tampilkan hasil prediksi
print("\n=== Prediksi AQI 3 Hari ke Depan ===")
for _, row in future_df.iterrows():
    ts = now + timedelta(hours=_ + 1)
    ts_str = ts.strftime("%Y-%m-%d %H:%M")
    aq = round(row['predicted_aqi'], 2)
    print(f"{ts_str}: AQI ≈ {aq}")
