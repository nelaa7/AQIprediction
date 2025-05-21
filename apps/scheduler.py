# import logging
# import atexit
# from django_apscheduler.jobstores import DjangoJobStore, register_events
# from apscheduler.schedulers.background import BackgroundScheduler
# from django.core.management import call_command
# from django.conf import settings

# # Setup logger
# logger = logging.getLogger('aqi_auto')

# # Buat scheduler instance
# scheduler = BackgroundScheduler()
# scheduler.add_jobstore(DjangoJobStore(), "default")

# def train_aqi_daily():
#     """Training harian dengan data 30 hari terakhir"""
#     try:
#         logger.info("🚀 [DAILY] Memulai training AQI harian...")
#         call_command('train_aqi', '--days', '30')
#         logger.info("✅ [DAILY] Training harian selesai")
#     except Exception as e:
#         logger.error(f"❌ [DAILY] Error training: {e}")

# def train_aqi_weekly():
#     """Training mingguan dengan data 90 hari terakhir"""
#     try:
#         logger.info("🚀 [WEEKLY] Memulai training AQI mingguan...")
#         call_command('train_aqi', '--days', '90')
#         logger.info("✅ [WEEKLY] Training mingguan selesai")
#     except Exception as e:
#         logger.error(f"❌ [WEEKLY] Error training: {e}")

# def predict_aqi_regular():
#     """Prediksi regular setiap 4 jam"""
#     try:
#         logger.info("🔮 [PREDICT] Membuat prediksi AQI...")
#         # Assuming you have a predict command or will create one
#         # call_command('predict_aqi')
        
#         # Atau bisa langsung prediksi di sini:
#         from apps.models import AQILog  # Adjust import
#         import pandas as pd
#         import joblib
#         import os
        
#         if os.path.exists('models/rf_day1.pkl'):
#             # Load model
#             model1 = joblib.load('models/rf_day1.pkl')
#             model2 = joblib.load('models/rf_day2.pkl')
#             model3 = joblib.load('models/rf_day3.pkl')
            
#             # Get latest data
#             latest = AQILog.objects.latest('timestamp')
#             features = ['pm25', 'pm10', 'co', 'no2', 'so2', 'o3']
            
#             # Create prediction data
#             import numpy as np
#             data = []
#             for feature in features:
#                 data.append(getattr(latest, feature, 0))
            
#             prediction_data = np.array(data).reshape(1, -1)
            
#             # Make predictions
#             pred1 = model1.predict(prediction_data)[0]
#             pred2 = model2.predict(prediction_data)[0]
#             pred3 = model3.predict(prediction_data)[0]
            
#             logger.info(f"📅 Prediksi Besok: {pred1:.2f}")
#             logger.info(f"📅 Prediksi Lusa: {pred2:.2f}")
#             logger.info(f"📅 Prediksi 3 Hari: {pred3:.2f}")
#         else:
#             logger.warning("⚠️ Model belum tersedia, jalankan training dulu")
            
#         logger.info("✅ [PREDICT] Prediksi selesai")
#     except Exception as e:
#         logger.error(f"❌ [PREDICT] Error prediksi: {e}")

# def start_scheduler():
#     """Mulai scheduler dengan semua jobs"""
    
#     # JOB 1: Training harian setiap jam 2 pagi
#     scheduler.add_job(
#         train_aqi_daily,
#         'cron',
#         hour=2,
#         minute=0,
#         id='daily_training',
#         max_instances=1,
#         replace_existing=True,
#         misfire_grace_time=900  # 15 menit tolerance
#     )
    
#     # JOB 2: Training mingguan setiap Minggu jam 3 pagi
#     scheduler.add_job(
#         train_aqi_weekly,
#         'cron',
#         day_of_week='sun',
#         hour=3,
#         minute=0,
#         id='weekly_training',
#         max_instances=1,
#         replace_existing=True,
#         misfire_grace_time=1800  # 30 menit tolerance
#     )
    
#     # JOB 3: Prediksi setiap 4 jam
#     scheduler.add_job(
#         predict_aqi_regular,
#         'interval',
#         hours=4,
#         id='regular_prediction',
#         max_instances=1,
#         replace_existing=True,
#     )
    
#     # JOB 4: Training dengan data fresh setiap 12 jam (optional)
#     scheduler.add_job(
#         lambda: call_command('train_aqi', '--days', '60'),
#         'interval',
#         hours=12,
#         id='semi_daily_training',
#         max_instances=1,
#         replace_existing=True,
#     )
    
#     # Register event handlers
#     register_events(scheduler)
    
#     # Start scheduler
#     scheduler.start()
#     logger.info("🚀 [SCHEDULER] APScheduler dimulai dengan jobs:")
#     logger.info("   📅 Daily training: Setiap hari jam 02:00")
#     logger.info("   📅 Weekly training: Setiap Minggu jam 03:00")
#     logger.info("   🔮 Regular prediction: Setiap 4 jam")
#     logger.info("   🔄 Semi-daily training: Setiap 12 jam")
    
#     # Shutdown scheduler when Django shuts down
#     atexit.register(lambda: scheduler.shutdown(wait=False))

# def stop_scheduler():
#     """Stop scheduler"""
#     try:
#         scheduler.shutdown(wait=False)
#         logger.info("⏹️ [SCHEDULER] APScheduler dihentikan")
#     except Exception as e:
#         logger.error(f"❌ [SCHEDULER] Error stopping: {e}")