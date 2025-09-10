from .auth import auth_bp
from .user import user_bp
from .admin import admin_bp

# All blueprints to register
blueprints = [
    auth_bp,
    user_bp,
    admin_bp
]
