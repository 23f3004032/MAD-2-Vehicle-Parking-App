#==============================================================================
#                           AUTHENTICATION CONTROLLER
#                         User Registration & Login System
#==============================================================================
# Author: Student
# Description: Authentication blueprint for user registration and login
# Features: JWT token generation, password hashing, session caching
# Security: Secure password storage, token-based authentication
#==============================================================================

from flask import request, Blueprint, jsonify, g
from flask_jwt_extended import create_access_token, get_jwt_identity
from models import db, User
from extensions import cache
from decorators import login_required
from cache_strategy import (
    cache_user_data, CacheKeys, CacheInvalidator,
    monitor_performance, AdvancedCacheManager
)

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

#==============================================================================
#                           USER REGISTRATION
#==============================================================================

#------User signup endpoint------#
@auth_bp.route('/register', methods=['POST'])
@monitor_performance
def register():
    try:
        data = request.get_json()
        
        # Validation
        if not data or not all(k in data for k in ('email', 'fullname', 'password')):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check if user already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'User already exists with this email'}), 400
        
        # Create new user
        user = User(
            email=data['email'],
            fullname=data['fullname'],
            role='user'  # Default role
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        # Create access token
        access_token = create_access_token(identity=user.email)
        
        # Invalidate user-related caches
        CacheInvalidator.invalidate_user_cache(user.id)
        CacheInvalidator.invalidate_admin_cache()  # For user count updates
        
        return jsonify({
            'message': 'User registered successfully',
            'access_token': access_token,
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Registration failed'}), 500

#==============================================================================
#                           USER LOGIN
#==============================================================================

#------User login endpoint------#
@auth_bp.route('/login', methods=['POST'])
@monitor_performance
def login():
    try:
        data = request.get_json()
        
        # Validation
        if not data or not all(k in data for k in ('email', 'password')):
            return jsonify({'error': 'Email and password required'}), 400
        
        # Find user
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Create access token
        access_token = create_access_token(identity=user.email)
        
        # Cache user session data for quick access
        cache_key = CacheKeys.user_session(user.id)
        cache.set(cache_key, {
            'user_id': user.id,
            'email': user.email,
            'role': user.role,
            'fullname': user.fullname
        }, timeout=3600)  # Cache for 1 hour
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': user.to_dict()
        }), 200
      
    except Exception as e:
        return jsonify({'error': 'Login failed'}), 500

#==============================================================================
#                           USER PROFILE ACCESS
#==============================================================================

#------Get current user information------#
@auth_bp.route('/me', methods=['GET'])
@login_required
@cache_user_data(timeout=1800)  # Cache for 30 minutes - user profile data
@monitor_performance
def get_current_user():
    try:
        return jsonify({
            'user': g.current_user.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get user info'}), 500
    
#----------------------------------------------------------------------------#
#------------Useful for checking if JWT  is still valid----------------------#
#----------------------------------------------------------------------------#
@auth_bp.route('/verify-token', methods=['POST'])
@login_required
def verify_token():
    try:
        return jsonify({
            'valid': True,
            'user': g.current_user.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'valid': False}), 401
