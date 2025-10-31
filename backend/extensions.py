#==============================================================================
#                           FLASK EXTENSIONS SETUP
#                         Centralized Extension Configuration
#==============================================================================
# Description: Central place to initialize all Flask extensions
# Pattern: Application factory pattern - extensions created empty first
# Usage: Extensions are configured when init_app(app) is called in app.py
#==============================================================================

from flask_caching import Cache
from celery import Celery
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_jwt_extended import JWTManager

#------Initialize all extensions (empty first, configured in app.py)------#
db = SQLAlchemy()           # Database ORM
mail = Mail()               # Email sending
cache = Cache()
celery = Celery()
jwt = JWTManager()
