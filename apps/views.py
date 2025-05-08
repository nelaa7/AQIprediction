from django.shortcuts import render
from datetime import datetime, date, timedelta
from apps.models import AQILog

# Create your views here.

def index(request):
    today = date.today
    day_one = date.today() + timedelta(days=1)
    day_two = date.today() + timedelta(days=2)
    day_three = date.today() + timedelta(days=3)
    
    aqi = AQILog.objects.order_by('-log_date').first()

    
    context ={
        'title' : 'AQI',
        'today' : today,
        'day_one' : day_one,
        'day_two' : day_two,
        'day_three' :day_three,
        'aqi':aqi,
        
    }
    return render (request, 'index.html', context)