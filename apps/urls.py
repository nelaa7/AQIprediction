from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.index, name='index'),
    path('chart-dominan', views.get_chat_data_dominan, name='chart-dominan'),
    path('get_chart_data_polutan', views.get_chart_data_polutan, name='get_chart_data_polutan'),
    path('article/<slug:slug>/', views.ArticleDetailView.as_view(), name='article-detail'),
    path('article', views.article_list, name='article_list'),
    path('about', views.about, name='about'),

    # path('article/<slug:slug>/', views.article_detail, name='details')


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)