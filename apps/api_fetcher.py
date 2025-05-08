import requests
from datetime import datetime
import os
import django

# Inisialisasi Django (jika dijalankan dari luar manajemen command)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AQIprediction.settings')  
django.setup()

from apps.models import AQILog  

URL = "https://api.waqi.info/feed/A420154/?token=b0a0842951c0c5e38d053830aa4c727e5dcfc9bb"

def get_aqi_data():
    try:
        response = requests.get(URL)
        data = response.json()

        if data["status"] != "ok":
            print("Gagal ambil data:", data["data"])
            return None

        d = data["data"]
        time_str = d["time"]["s"]

        return {
            "timestamp": datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S"),
            "location": d["attributions"][0].get("station"),
            "aqi": d["aqi"],
            "dominan": d["dominentpol"],
            "pm25": d["iaqi"].get("pm25", {}).get("v"),
            "pm10": d["iaqi"].get("pm10", {}).get("v"),
            "co": d["iaqi"].get("co", {}).get("v"),
            "no2": d["iaqi"].get("no2", {}).get("v"),
            "so2": d["iaqi"].get("so2", {}).get("v"),
            "o3": d["iaqi"].get("o3", {}).get("v")
        }
    except Exception as e:
        print("Error:", e)
        return None

def save_to_db(data):
    AQILog.objects.create(**data)
    print("Data AQI berhasil disimpan ke database.")

if __name__ == "__main__":
    data = get_aqi_data()
    if data:
        save_to_db(data)
