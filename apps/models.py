from django.db import models



class AQILog(models.Model):
    log_date = models.DateTimeField(auto_now_add=True)
    timestamp = models.DateTimeField()
    location = models.CharField(max_length=255)
    dominan = models.CharField(max_length=10)
    aqi = models.CharField(null=True, blank=True)
    pm25 = models.CharField(null=True, blank=True)
    pm10 = models.CharField(null=True, blank=True)
    co = models.CharField(null=True, blank=True)
    no2 = models.CharField(null=True, blank=True)
    so2 = models.CharField(null=True, blank=True)
    o3 = models.CharField(null=True, blank=True)

    def __str__(self):
        return f"{self.log_date} - {self.timestamp} - AQI: {self.aqi}"