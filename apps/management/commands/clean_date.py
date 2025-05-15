# apps\management\commands\clean_date.py
from django.http import JsonResponse
from apps.models import aqi_data
import pandas as pd

def bersihkan_data_aqi_data(request):
    qs = aqi_data.objects.all().values()
    df = pd.DataFrame(qs)

    # Preprocessing
    df['dominan'] = df['dominan'].fillna('Tidak Diketahui')
    df['aqi'] = df['aqi'].fillna(0).astype(int)
    df['pm25'] = df['pm25'].fillna(0).astype(int)
    df['pm10'] = df['pm10'].fillna(0).astype(int)
    df['co'] = df['co'].fillna(0).astype(int)
    df['no2'] = df['no2'].fillna(0).astype(int)
    df['so2'] = df['so2'].fillna(0).astype(int)
    df['o3'] = df['o3'].fillna(0).astype(int)
    df = df.drop_duplicates(subset=['dominan'])

    # Simpan balik ke DB
    for _, row in df.iterrows():
        aqi_data.objects.update_or_create(
            id=row['id'],
            defaults={
                'dominan': row['dominan'],
                'aqi': row['aqi'],
                'pm25': row['pm25'],
                'pm10': row['pm10'],
                'co': row['co'],
                'no2': row['no2'],
                'so2': row['so2'],
                'o3': row['o3'],
            }
        )

    return JsonResponse({'status': 'berhasil dibersihkan', 'jumlah_data': len(df)})
