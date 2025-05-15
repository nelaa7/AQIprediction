from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='index'),
    path('chart-dominan', views.get_chat_data_dominan, name='chart-dominan'),
    path('get_chart_data_polutan', views.get_chart_data_polutan, name='get_chart_data_polutan'),
]