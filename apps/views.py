from django.http import JsonResponse
from django.shortcuts import render
from datetime import datetime, date, timedelta
import joblib
import pandas as pd
from apps.models import AQILog, Article, PredictedAQI
from django.db.models import Count, Q
from django.db.models import Avg
from django.utils.timezone import now
from django.views.generic import DetailView

class ArticleDetailView(DetailView):
    model = Article
    template_name = 'article_detail.html'  # file template untuk detail
    context_object_name = 'article'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ambil semua artikel lain, kecuali yang sedang dilihat
        context['other_articles'] = Article.objects.exclude(id=self.object.id).order_by('-timestamp')[:5]
        return context

# Create your views here.
FEATURES = ['pm25', 'pm10', 'co', 'no2', 'so2', 'o3']

def index(request):
    today = date.today
    day_one = date.today() + timedelta(days=1)
    day_two = date.today() + timedelta(days=2)
    day_three = date.today() + timedelta(days=3)
    
    aqi = AQILog.objects.order_by('-log_date').first()
    
    total_data = AQILog.objects.all().count
    # tidak_terdeteksi = AQILog.objects.filter(aqi='-').count
    
    pm25 = AQILog.objects.filter(pm25__regex=r'^\d+(\.\d+)?$').count()
    co = AQILog.objects.filter(co__regex=r'^\d+(\.\d+)?$').count()
    o3 = AQILog.objects.filter(o3__regex=r'^\d+(\.\d+)?$').count()
    pm10 = AQILog.objects.filter(pm10__regex=r'^\d+(\.\d+)?$').count()
    no2 = AQILog.objects.filter(no2__regex=r'^\d+(\.\d+)?$').count()
    so2 = AQILog.objects.filter(so2__regex=r'^\d+(\.\d+)?$').count()
    predictions = PredictedAQI.objects.order_by('timestamp')
    
    #3 hari kedepan
    latest_log = AQILog.objects.order_by('-timestamp').first()
    if not latest_log:
        return render(request, 'predict_aqi.html', {'error': 'Data AQI tidak ditemukan.'})
    
    input_data = {
        'pm25': latest_log.pm25,
        'pm10': latest_log.pm10,
        'co': latest_log.co,
        'no2': latest_log.no2,
        'so2': latest_log.so2,
        'o3': latest_log.o3,
    }
    
    
    df_input = pd.DataFrame([input_data], columns=FEATURES)
    model1 = joblib.load("models/rf_day1.pkl")
    model2 = joblib.load("models/rf_day2.pkl")
    model3 = joblib.load("models/rf_day3.pkl")
    
    pred1 = model1.predict(df_input)[0]
    pred2 = model2.predict(df_input)[0]
    pred3 = model3.predict(df_input)[0]
    
    article = Article.objects.all()[:3]
    
    context ={
        'title' : 'AQI',
        'today' : today,
        'day_one' : day_one,
        'day_two' : day_two,
        'day_three' :day_three,
        'aqi':aqi,
        'total_data':total_data,
        # 'tidak_terdeteksi':tidak_terdeteksi,
        'pm25':pm25,
        'co2':co,
        'o3':o3,
        'pm10':pm10,
        'no2':no2,
        'so2':so2,
        'predictions':predictions,
        # 'daily_predictions': result,
        'prediksi_besok': round(pred1),
        'prediksi_lusa': round(pred2),
        'prediksi_3hari': round(pred3),
        'input_data': input_data,
        'tanggal_besok': latest_log.timestamp + timedelta(days=1),
        'tanggal_lusa': latest_log.timestamp + timedelta(days=2),
        'tanggal_3hari': latest_log.timestamp + timedelta(days=3),
        'article':article,
        
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
   
def article_list(request):
    article_list = Article.objects.all()
    
    context ={
        'title': 'Article',
        'article_list': article_list,
    }
    
    return render (request, 'article_list.html', context)

def about(request):
    
    context={
        'title': 'About us',
        
    }
    return render (request, 'about.html', context)

    # today = now().date()
    # three_days = [today + timedelta(days=i) for i in range(1, 4)]  # besok sampai 3 hari ke depan

    # result = []

    # for day in three_days:
    #     day_data = PredictedAQI.objects.filter(timestamp__date=day)
    #     avg_aqi = day_data.aggregate(avg_aqi=Avg('predicted_aqi'))['avg_aqi']

    #     result.append({
    #         'date': day,
    #         'average_aqi': round(avg_aqi, 2) if avg_aqi else None
    #     })