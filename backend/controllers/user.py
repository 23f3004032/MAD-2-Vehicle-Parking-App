from flask import Blueprint, jsonify, g, request
from models import db, User, ReserveSpot, Lot, Spot
from extensions import cache
from decorators import login_required
from datetime import datetime, timezone

user_bp = Blueprint('user', __name__, url_prefix='/api/user')

@user_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    try:
        return jsonify({
            'user': g.current_user.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get profile'}), 500

@user_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    try:
        data = request.get_json()
        
        if 'fullname' in data:
            g.current_user.fullname = data['fullname']
        if 'address' in data:
            g.current_user.address = data['address']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': g.current_user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update profile'}), 500

@user_bp.route('/dashboard-stats', methods=['GET'])
@login_required
def get_dashboard_stats():
    try:
        user_id = g.current_user.id
        
        # Get user reservations
        total_reservations = ReserveSpot.query.filter_by(user_id=user_id).count()
        active_reservations = ReserveSpot.query.filter_by(
            user_id=user_id, 
            leaving_time=None
        ).count()
        
        # Calculate total spent
        completed_reservations = ReserveSpot.query.filter(
            ReserveSpot.user_id == user_id,
            ReserveSpot.leaving_time.isnot(None)
        ).all()
        
        total_spent = sum(r.cost or 0 for r in completed_reservations)
        
        return jsonify({
            'total_reservations': total_reservations,
            'active_reservations': active_reservations,
            'total_spent': total_spent,
            'completed_reservations': len(completed_reservations)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get dashboard stats'}), 500
