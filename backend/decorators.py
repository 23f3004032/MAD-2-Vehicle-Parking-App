#==============================================================================
#                           AUTHENTICATION DECORATORS
#                         Access Control & Security Wrappers
#==============================================================================
# Description: Custom decorators to control who can access API endpoints
# Features: Login required, admin-only access, JWT token verification
# Usage: Apply @login_required or @admin_required to protect routes
#==============================================================================
from functools import wraps
from flask import abort, g
from models import User
from flask_jwt_extended import get_jwt_identity, jwt_required

#========================= LOGIN REQUIRED DECORATOR ========================#
def login_required(f):
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        email = get_jwt_identity()
        user = User.query.filter_by(email=email).first()
        if not user:
            abort(401)
        g.current_user = user
        return f(*args, **kwargs)
    return decorated_function

#---------------------------------------------------------------------------#
#-------------------------Wrapper for logged in admin -----------------------#
#---------------------------------------------------------------------------#
def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if g.current_user.role != 'admin':
            abort(403, {'error': 'Admin access required!'})
        return f(*args, **kwargs)
    return decorated_function
