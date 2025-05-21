from django.contrib import admin
from apps.models import AQILog, Article
from django import forms
from ckeditor.widgets import CKEditorWidget

# Register your models here.

@admin.register(AQILog)
class AQI(admin.ModelAdmin):
    list_display=['log_date', 'timestamp', 'location', 'aqi', 'dominan', 'pm25', 'pm10', 'co', 'no2', 'so2', 'o3']
    search_fields=['dominan']
    list_filter=['log_date']
    
class ArticleAdminForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = Article
        fields = '__all__'

class ArticleAdmin(admin.ModelAdmin):
    form = ArticleAdminForm
    list_display = ('name', 'slug', 'timestamp')

admin.site.register(Article, ArticleAdmin)
    
    