import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

def preprocess_for_ml(location=None, start_date=None, end_date=None):
    from apps.models import AQILog
    
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

    # Buat fitur baru dari timestamp, misalnya jam dan hari
    df['hour'] = df['timestamp'].dt.hour
    df['day'] = df['timestamp'].dt.dayofweek  # 0=Monday, 6=Sunday

    # Pilih fitur untuk training dan target
    X = df[features + ['hour', 'day']]
    y = df['aqi']

    # Split data train dan test (80% train, 20% test)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Scaling fitur numeric dengan StandardScaler
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    return X_train_scaled, X_test_scaled, y_train, y_test
