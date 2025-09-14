#This is a package initializer for my app’s route modules.
#It imports all blueprints (auth, user, admin, analytics) and stores them in a list.

from .auth import auth_bp
from .user import user_bp
from .admin import admin_bp
from .analytics import analytics_bp

# All blueprints to register
blueprints = [
    auth_bp,
    user_bp,
    admin_bp,
    analytics_bp
]
