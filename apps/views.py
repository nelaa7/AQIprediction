from django.http import JsonResponse
from django.shortcuts import render
from datetime import datetime, date, timedelta
from apps.models import AQILog
from django.db.models import Count, Q

# Create your views here.

def index(request):
    today = date.today
    day_one = date.today() + timedelta(days=1)
    day_two = date.today() + timedelta(days=2)
    day_three = date.today() + timedelta(days=3)
    
    aqi = AQILog.objects.order_by('-log_date').first()
    
    total_data = AQILog.objects.all().count
    tidak_terdeteksi = AQILog.objects.filter(aqi='-').count
    
    pm25 = AQILog.objects.filter(pm25__regex=r'^\d+(\.\d+)?$').count()
    co = AQILog.objects.filter(co__regex=r'^\d+(\.\d+)?$').count()
    o3 = AQILog.objects.filter(o3__regex=r'^\d+(\.\d+)?$').count()
    pm10 = AQILog.objects.filter(pm10__regex=r'^\d+(\.\d+)?$').count()
    no2 = AQILog.objects.filter(no2__regex=r'^\d+(\.\d+)?$').count()
    so2 = AQILog.objects.filter(so2__regex=r'^\d+(\.\d+)?$').count()





    
    aqi.aqi = int(aqi.aqi)    
    bg_aqi = AQILog.aqi
    

    
    context ={
        'title' : 'AQI',
        'today' : today,
        'day_one' : day_one,
        'day_two' : day_two,
        'day_three' :day_three,
        'aqi':aqi,
        'total_data':total_data,
        'tidak_terdeteksi':tidak_terdeteksi,
        'pm25':pm25,
        'co2':co,
        'o3':o3,
        'pm10':pm10,
        'no2':no2,
        'so2':so2
        
    }
    return render (request, 'index.html', context)

def get_chart_data_polutan(request):
    data = {
        'pm25' : AQILog.objects.filter(pm25__regex=r'^\d+(\.\d+)?$').count(),
        'pm10' : AQILog.objects.filter(pm10__regex=r'^\d+(\.\d+)?$').count(),
        'co' : AQILog.objects.filter(co__regex = r'^-?\d+(\.\d+)?$').count(),
        'no2' : AQILog.objects.filter(no2__regex=r'^\d+(\.\d+)?$').count(),
        'so2' : AQILog.objects.filter(so2__regex=r'^\d+(\.\d+)?$').count(),
        'o3' : AQILog.objects.filter(o3__regex=r'^\d+(\.\d+)?$').count(),
        
    }
    labels = [key.upper() for key in data.keys()]

    # labels = list(data.keys())  # Ambil nama polutan
    values = list(data.values())  # Ambil jumlah per polutan

    return JsonResponse({
        'labels': labels,
        'values': values,
    })
    
def get_chat_data_dominan(request):
    POLUTAN_LIST = ['pm25', 'pm10', 'co', 'no2', 'so2', 'o3']

    # Hitung jumlah tiap dominan
    data = AQILog.objects.values('dominan').annotate(jumlah=Count('dominan'))

    # Buat dict: {'pm25': 10, 'co': 3, ...}
    data_dict = {item['dominan'].lower(): item['jumlah'] for item in data if item['dominan']}

    labels = [pol.upper() for pol in POLUTAN_LIST]
    values = [data_dict.get(pol, 0) for pol in POLUTAN_LIST]

    # Hitung total terdeteksi dan tidak terdeteksi
    total_terdeteksi = AQILog.objects.exclude(dominan__isnull=True).exclude(dominan='').count()
    total_tidak_terdeteksi = AQILog.objects.filter(Q(dominan__isnull=True) | Q(dominan='')).count()

    return JsonResponse({
        'labels': labels,
        'values': values,
        'keterangan': {
            'terdeteksi': total_terdeteksi,
            'tidak_terdeteksi': total_tidak_terdeteksi,
            'total': total_terdeteksi + total_tidak_terdeteksi,
        }
    })