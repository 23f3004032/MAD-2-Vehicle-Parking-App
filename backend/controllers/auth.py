#this auth.py is my authentication blueprint.

from flask import request, Blueprint, jsonify, g
from flask_jwt_extended import create_access_token, get_jwt_identity
from models import db, User
from extensions import cache
from decorators import login_required

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

#---------------------------------------------------------------------------#
#-------------------------Signup Route---------------------------------------#
#---------------------------------------------------------------------------#
@auth_bp.route('/register', methods=['POST'])
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
        
        return jsonify({
            'message': 'User registered successfully',
            'access_token': access_token,
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Registration failed'}), 500

#---------------------------------------------------------------------------#
#-------------------------Login Route---------------------------------------#
#---------------------------------------------------------------------------#
@auth_bp.route('/login', methods=['POST'])
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
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': user.to_dict()
        }), 200
      
    except Exception as e:
        return jsonify({'error': 'Login failed'}), 500

#---------------------------------------------------------------------------#
#----------User Info Route(Frontend fetch this to get user details)----------#
#----------------------------------------------------------------------------#
@auth_bp.route('/me', methods=['GET'])
@login_required
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
