import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

# ======== [1] Load Data dari CSV ========
df = pd.read_csv("aqi_jkt.csv")  # Ganti nama file sesuai dengan CSV kamu

# Pastikan kolom 'aqi' dan fitur lainnya ada
features = ['pm25', 'pm10', 'co', 'no2', 'so2', 'o3']

if df.isnull().sum().sum() > 0:
    print("=> Mengisi missing value dengan nilai rata-rata...")
    for col in features:
        df[col] = df[col].fillna(df[col].mean())

# Tambahkan fitur waktu jika ada kolom timestamp
# if 'timestamp' in df.columns:
#     df['timestamp'] = pd.to_datetime(df['timestamp'])
#     df['hour'] = df['timestamp'].dt.hour
#     df['day'] = df['timestamp'].dt.dayofweek
# else:
#     df['hour'] = 12  # default
#     df['day'] = 2    # default (misal Rabu)

# ======== [2] Label Kategori AQI ========
def category_aqi(aqi):
    if aqi <= 50:
        return 'Baik'
    elif aqi <= 100:
        return 'Sedang'
    elif aqi <= 200:
        return 'Tidak Sehat'
    elif aqi <= 300:
        return 'Sangat Tidak Sehat'
    else:
        return 'Berbahaya'

df['aqi_category'] = df['max'].apply(category_aqi)

# ======== [3] Train/Test Split dan Training ========
X = df[features ]
y = df['aqi_category']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.7, random_state=42
)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

# ======== [4] Classification Report ========
print("\n=== Classification Report ===")
print(classification_report(y_test, y_pred))

# ======== [5] Confusion Matrix ========
labels = sorted(y.unique())
cm = confusion_matrix(y_test, y_pred, labels=labels)

print("\n=== Confusion Matrix ===")
print("Actual \\ Pred".ljust(20), "  ".join(f"{l:15}" for l in labels))
for actual_label, row in zip(labels, cm):
    print(f"{actual_label:<20}  " + "  ".join(f"{val:<15}" for val in row))
