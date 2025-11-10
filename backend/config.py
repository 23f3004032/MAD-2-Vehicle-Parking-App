#==============================================================================
#                           ONLYPARK CONFIGURATION
#                         Application Settings & Environment
#==============================================================================
# Description: Configuration settings for database, cache, email, and Celery
# Features: Redis cache, Gmail SMTP, Celery scheduling, JWT authentication
#==============================================================================

import os
import pytz
from celery.schedules import crontab
from datetime import timedelta
from dotenv import load_dotenv

#------Load environment variables from .env file------#
load_dotenv()

#------Setup database path------#
basedir = os.path.abspath(os.path.dirname(__file__))
database_path = os.path.join(basedir, 'app.db')

#==============================================================================
#                          MAIN CONFIGURATION CLASS
#==============================================================================

class Config:
    #------Database Configuration------#
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{database_path}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    #------JWT Authentication Settings------#
    JWT_SECRET_KEY = 'MAD2-PROJECT-SECRET-KEY-CHANGE-IN-PRODUCTION'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    #------Redis Cache Configuration------#
    CACHE_TYPE = 'RedisCache'
    CACHE_REDIS_HOST = 'localhost'
    CACHE_REDIS_PORT = 6379
    CACHE_REDIS_DB = 0
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes default cache timeout
    
    #------Celery Background Task Configuration------#
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    CELERY_TIMEZONE = 'Asia/Kolkata'
    CELERY_ENABLE_UTC = False
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_RESULT_EXPIRES = 3600  # Results expire after 1 hour
    CELERY_TASK_TRACK_STARTED = True
    CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes max per task
    
    #------Development/Demo Task Execution------#
    # Note: Set CELERY_EAGER=False in .env for Beat scheduling to work
    CELERY_TASK_ALWAYS_EAGER = os.environ.get('CELERY_EAGER', 'False').lower() == 'true'
    CELERY_TASK_EAGER_PROPAGATES = True
    
    #------Email Configuration (Gmail SMTP)------#
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'onlyparks19@gmail.com'
    MAIL_PASSWORD = 'uhtoituvvedgxjps'  # Gmail App Password
    MAIL_DEFAULT_SENDER = 'onlyparks19@gmail.com'

    #------File Export Directory------#
    EXPORT_DIR = os.path.join(basedir, 'exports')
    
    #------Celery Beat Scheduled Tasks------#
    CELERY_BEAT_SCHEDULE = {
        'daily-reminder-job': {
            'task': 'tasks.send_daily_reminders',
            'schedule': crontab(hour='18',minute='0'),  # Every day at 6 PM
        },
        'monthly-report-job': {
            'task': 'tasks.generate_all_monthly_reports',
            'schedule': crontab(day_of_month='1', hour=1, minute=0),  # 1st of every month at 1 AM
        },
    }