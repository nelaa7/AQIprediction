# from django.core.management.base import BaseCommand
# from django.utils import timezone

# class SCommand(BaseCommand):
#     help = 'Kontrol APScheduler untuk AQI'
    
#     def add_arguments(self, parser):
#         parser.add_argument(
#             'action',
#             choices=['status', 'jobs', 'run-now', 'clear'],
#             help='Aksi yang ingin dilakukan'
#         )
#         parser.add_argument(
#             '--job-id',
#             type=str,
#             help='ID job untuk run-now'
#         )
    
#     def handle(self, *args, **options):
#         action = options['action']
        
#         if action == 'status':
#             self.show_status()
#         elif action == 'jobs':
#             self.show_jobs()
#         elif action == 'run-now':
#             self.run_job_now(options.get('job_id'))
#         elif action == 'clear':
#             self.clear_jobs()
    
#     def show_status(self):
#         from django_apscheduler.models import DjangoJob
        
#         total_jobs = DjangoJob.objects.count()
#         active_jobs = DjangoJob.objects.filter(next_run_time__isnull=False).count()
        
#         if total_jobs > 0:
#             self.stdout.write(self.style.SUCCESS("🟢 APScheduler aktif"))
#             self.stdout.write(f"📊 Total jobs: {total_jobs}")
#             self.stdout.write(f"🟢 Active jobs: {active_jobs}")
#         else:
#             self.stdout.write(self.style.WARNING("🟡 Tidak ada jobs terdaftar"))
    
#     def show_jobs(self):
#         from django_apscheduler.models import DjangoJob
        
#         jobs = DjangoJob.objects.all().order_by('next_run_time')
        
#         if not jobs:
#             self.stdout.write("📭 Tidak ada jobs")
#             return
        
#         self.stdout.write("📋 Daftar Jobs:")
#         for job in jobs:
#             status = "🟢" if job.next_run_time else "🔴"
#             next_run = job.next_run_time.strftime('%Y-%m-%d %H:%M:%S') if job.next_run_time else 'Tidak terjadwal'
#             self.stdout.write(f"  {status} {job.id} - Next: {next_run}")
    
#     def run_job_now(self, job_id):
#         if not job_id:
#             self.stdout.write(self.style.ERROR("❌ Specify job ID dengan --job-id"))
#             return
        
#         # Manual trigger berdasarkan job_id
#         try:
#             if job_id == 'daily_training':
#                 from apps.scheduler import train_aqi_daily
#                 train_aqi_daily()
#             elif job_id == 'weekly_training':
#                 from apps.scheduler import train_aqi_weekly
#                 train_aqi_weekly()
#             elif job_id == 'regular_prediction':
#                 from apps.scheduler import predict_aqi_regular
#                 predict_aqi_regular()
#             else:
#                 self.stdout.write(f"❌ Job ID tidak dikenal: {job_id}")
#                 return
                
#             self.stdout.write(f"✅ Job {job_id} dijalankan secara manual")
#         except Exception as e:
#             self.stdout.write(f"❌ Error menjalankan job: {e}")
    
#     def clear_jobs(self):
#         from django_apscheduler.models import DjangoJob
        
#         count = DjangoJob.objects.count()
#         DjangoJob.objects.all().delete()
#         self.stdout.write(f"🗑️ {count} jobs dihapus")
