import os
from celery.schedules import crontab
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))
database_path = os.path.join(basedir, 'app.db')

class Config:
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{database_path}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'MAD2-PROJECT-SECRET-KEY-CHANGE-IN-PRODUCTION'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # Redis Configuration
    CACHE_TYPE = 'RedisCache'
    CACHE_REDIS_HOST = 'localhost'
    CACHE_REDIS_PORT = 6379
    CACHE_REDIS_DB = 0
    CACHE_DEFAULT_TIMEOUT = 300
    
    # Celery Configuration
    CELERY_BROKER_URL = 'redis://localhost:6379/1'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/2'
    CELERY_TIMEZONE = 'Asia/Kolkata'
    CELERY_ENABLE_UTC = False
    
    # Email Configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'your-email@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'your-app-password'
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME') or 'your-email@gmail.com'
    
    # Export Directory
    EXPORT_DIR = os.path.join(basedir, 'exports')
    
    # Celery Beat Schedule
    CELERY_BEAT_SCHEDULE = {
        'daily-reminder-job': {
            'task': 'tasks.send_daily_reminders',
            'schedule': crontab(hour=18, minute=0),  # 6 PM every day
        },
        'monthly-report-job': {
            'task': 'tasks.generate_all_monthly_reports',
            'schedule': crontab(hour=1, minute=0, day_of_month='1'),  # 1st of every month
        },
    }
