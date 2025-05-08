from django.contrib import admin
from apps.models import AQILog

# Register your models here.

@admin.register(AQILog)
class AQI(admin.ModelAdmin):
    list_display=['log_date', 'timestamp', 'location', 'aqi', 'dominan', 'pm25', 'pm10', 'co', 'no2', 'so2', 'o3']
    search_fields=['dominan']
    list_filter=['log_date']
    
    