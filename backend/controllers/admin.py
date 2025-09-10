from flask import Blueprint, jsonify, g, request
from models import db, User, Lot, Spot, ReserveSpot
from extensions import cache
from decorators import login_required, admin_required
from datetime import datetime, timezone

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@admin_bp.route('/dashboard-stats', methods=['GET'])
@admin_required
def get_admin_dashboard_stats():
    try:
        # Get basic counts
        total_users = User.query.filter_by(role='user').count()
        total_lots = Lot.query.count()
        total_spots = Spot.query.count()
        occupied_spots = Spot.query.filter_by(status='O').count()
        available_spots = total_spots - occupied_spots
        
        # Get revenue
        total_revenue = db.session.query(db.func.sum(ReserveSpot.cost)).scalar() or 0
        
        # Get recent bookings
        recent_bookings = ReserveSpot.query.order_by(
            ReserveSpot.parking_time.desc()
        ).limit(5).all()
        
        return jsonify({
            'total_users': total_users,
            'total_lots': total_lots,
            'total_spots': total_spots,
            'occupied_spots': occupied_spots,
            'available_spots': available_spots,
            'total_revenue': total_revenue,
            'recent_bookings': [booking.to_dict() for booking in recent_bookings]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get admin stats'}), 500

@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_all_users():
    try:
        users = User.query.filter_by(role='user').all()
        return jsonify({
            'users': [user.to_dict() for user in users]
        }), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get users'}), 500
