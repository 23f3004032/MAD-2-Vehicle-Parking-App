#This file is a central place to create Flask 
#Extensions before they’re attached to the app.
#It follows the Flask application factory pattern, 
#Meaning extensions are initialized empty first and 
#Then configured when init_app(app) is called inside app.py 

from flask_caching import Cache
from celery import Celery
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_jwt_extended import JWTManager

# Initialize extensions
db = SQLAlchemy()
mail = Mail()
cache = Cache()
celery = Celery()
jwt = JWTManager()
