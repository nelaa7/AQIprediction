from django.db import models
from ckeditor.fields import RichTextField
from django.utils.text import slugify

class AQILog(models.Model):
    log_date = models.DateTimeField(auto_now_add=True)
    timestamp = models.DateTimeField()
    location = models.CharField(max_length=255)
    dominan = models.CharField(max_length=10)
    aqi = models.IntegerField(null=True, blank=True) 
    pm25 = models.FloatField(null=True, blank=True)
    pm10 = models.FloatField(null=True, blank=True)
    co = models.FloatField(null=True, blank=True)
    no2 = models.FloatField(null=True, blank=True)
    so2 = models.FloatField(null=True, blank=True)
    o3 = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.log_date} - {self.timestamp} - AQI: {self.aqi}"

class Data_aqi(models.Model):
    timestamp = models.DateTimeField()
    location = models.CharField(max_length=255)
    dominan = models.CharField(max_length=10)
    aqi = models.IntegerField(null=True, blank=True) 
    pm25 = models.FloatField(null=True, blank=True)
    pm10 = models.FloatField(null=True, blank=True)
    co = models.FloatField(null=True, blank=True)
    no2 = models.FloatField(null=True, blank=True)
    so2 = models.FloatField(null=True, blank=True)
    o3 = models.FloatField(null=True, blank=True)


    def __str__(self):
        return f"{self.log_date} - {self.timestamp} - AQI: {self.aqi}"
    
class PredictedAQI(models.Model):
    timestamp = models.DateTimeField(unique=True)
    predicted_aqi = models.FloatField()

    def __str__(self):
        return f"{self.timestamp} - {self.predicted_aqi}"
    
class Article(models.Model):
    name = models.CharField(null=False)
    slug = models.SlugField(unique=True, blank=True, max_length=225)
    thumbnail = models.ImageField(upload_to='thumbnails/')
    content = RichTextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:  # hanya isi slug jika belum ada
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name}"
    
    