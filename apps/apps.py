from django.apps import AppConfig
import os


class AppsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps'
    
    # def ready(self):
    #     # Import and start scheduler only in main process
    #     # Hindari duplikasi saat auto-reload development
    #     if os.environ.get('RUN_MAIN', None) != 'true':
    #         return
            
    #     try:
    #         from . import scheduler
    #         scheduler.start_scheduler()
    #     except Exception as e:
    #         print(f"❌ Error starting scheduler: {e}")
