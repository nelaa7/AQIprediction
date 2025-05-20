from django.core.management.base import BaseCommand
import requests
from datetime import datetime
from apps.models import AQILog 
import schedule
import time

URL = f"https://api.waqi.info/feed/A420154/?token=b0a0842951c0c5e38d053830aa4c727e5dcfc9bb"

def safe_int(value):
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

def safe_float(value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

class Command(BaseCommand):
    help = 'Fetch AQI data and save it to the database every hour'
    
    
    
    def __init__(self):
        super().__init__()
        self.counter = 0 

    def handle(self, *args, **kwargs):
        # Jadwalkan job setiap 1 jam
        schedule.every(15).minutes.do(self.job)

        self.stdout.write(self.style.SUCCESS("Scheduler berjalan. Menunggu 15 menit pertama..."))

        while True:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.stdout.write(self.style.HTTP_INFO(f"[{now}] Menunggu proses pengambilan data ..."))
            schedule.run_pending()
            time.sleep(1)

    def job(self):
        self.counter += 1  
        self.stdout.write(self.style.WARNING(f"===> Pengambilan data ke-{self.counter}"))
        data = self.get_aqi_data()
        if data:
            self.save_to_db(data)
            self.stdout.write(self.style.SUCCESS(f"Data berhasil disimpan: {data}"))
        else:
            self.stdout.write(self.style.ERROR("Gagal ambil data"))

    def get_aqi_data(self):
        try:
            response = requests.get(URL)
            data = response.json()

            if data["status"] != "ok":
                return None

            d = data["data"]
            time_str = d["time"]["s"]

            return {
                "log_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "timestamp": time_str,
                "location": d["attributions"][0].get("station"),
                "aqi": safe_int(d.get("aqi")),
                "dominan": d.get("dominentpol"),
                "pm25": safe_float(d["iaqi"].get("pm25", {}).get("v")),
                "pm10": safe_float(d["iaqi"].get("pm10", {}).get("v")),
                "co": safe_float(d["iaqi"].get("co", {}).get("v")),
                "no2": safe_float(d["iaqi"].get("no2", {}).get("v")),
                "so2": safe_float(d["iaqi"].get("so2", {}).get("v")),
                "o3": safe_float(d["iaqi"].get("o3", {}).get("v")),
            }
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))
            return None

    def save_to_db(self, data):
        AQILog.objects.create(
            log_date=data['log_date'],
            timestamp=data['timestamp'],
            location=data['location'],
            aqi=data['aqi'],
            dominan=data['dominan'],
            pm25=data['pm25'],
            pm10=data['pm10'],
            co=data['co'],
            no2=data['no2'],
            so2=data['so2'],
            o3=data['o3']
        )
