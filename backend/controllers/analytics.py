#==============================================================================
#                           ANALYTICS CONTROLLER
#                         Business Intelligence & Reporting
#==============================================================================
# Author: Student
# Description: Analytics endpoints for admin and user dashboards
# Features: Revenue tracking, usage patterns, performance metrics, charts data
# Caching: Intelligent caching with different timeouts for various data types
#==============================================================================

from flask import Blueprint, jsonify, g, request
from models import db, User, ReserveSpot, Lot, Spot
from decorators import login_required, admin_required
from datetime import datetime, timezone, timedelta
from sqlalchemy import func, and_, extract
from collections import defaultdict
from cache_strategy import (
    cache_admin_data, cache_user_data, CacheKeys, CacheInvalidator,
    monitor_performance, AdvancedCacheManager
)

analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')

#==============================================================================
#                           UTILITY FUNCTIONS
#==============================================================================

#------Timezone handling for analytics------#
def ensure_timezone_aware(dt):
    """Ensure datetime is timezone-aware for consistent analytics"""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt

#==============================================================================
#                           ADMIN ANALYTICS DASHBOARD
#==============================================================================

#------Admin overview statistics------#

@analytics_bp.route('/admin/overview', methods=['GET'])
@admin_required
@cache_admin_data(timeout=600)  # Cache for 10 minutes - overview data changes slowly
@monitor_performance
def admin_overview():
    try:
        # Total revenue
        total_revenue = db.session.query(func.sum(ReserveSpot.cost)).filter(
            ReserveSpot.cost.isnot(None)
        ).scalar() or 0
        
        # Total bookings
        total_bookings = ReserveSpot.query.count()
        
        # Active bookings (not released)
        active_bookings = ReserveSpot.query.filter_by(leaving_time=None).count()
        
        # Total users
        total_users = User.query.filter_by(role='user').count()
        
        # Average booking duration (completed bookings only)
        completed_bookings = ReserveSpot.query.filter(ReserveSpot.leaving_time.isnot(None)).all()
        avg_duration = 0
        if completed_bookings:
            total_duration = 0
            for booking in completed_bookings:
                leaving_time = ensure_timezone_aware(booking.leaving_time)
                parking_time = ensure_timezone_aware(booking.parking_time)
                duration = (leaving_time - parking_time).total_seconds() / 3600
                total_duration += duration
            avg_duration = total_duration / len(completed_bookings)
        
        return jsonify({
            'total_revenue': round(total_revenue, 2),
            'total_bookings': total_bookings,
            'active_bookings': active_bookings,
            'total_users': total_users,
            'avg_duration_hours': round(avg_duration, 2)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get admin overview'}), 500

#==============================================================================
#                           ADMIN CHARTS & TRENDS
#==============================================================================

#------Revenue trends over time------#
@analytics_bp.route('/admin/revenue-trends', methods=['GET'])
@admin_required  
@cache_admin_data(timeout=900)  # Cache for 15 minutes - financial data
@monitor_performance
def revenue_trends():
    try:
        # Get date range from query params (default to last 30 days)
        days = int(request.args.get('days', 30))
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)
        
        # Get revenue by day
        revenue_by_date = db.session.query(
            func.date(ReserveSpot.parking_time).label('date'),
            func.sum(ReserveSpot.cost).label('revenue')
        ).filter(
            and_(
                ReserveSpot.parking_time >= start_date,
                ReserveSpot.parking_time <= end_date,
                ReserveSpot.cost.isnot(None)
            )
        ).group_by(func.date(ReserveSpot.parking_time)).all()
        
        # Format data for charts
        chart_data = {
            'labels': [],
            'revenue': []
        }
        
        # Create a dict for easy lookup
        revenue_dict = {str(item.date): float(item.revenue) for item in revenue_by_date}
        
        # Fill in all dates in range (including zeros)
        current_date = start_date.date()
        while current_date <= end_date.date():
            chart_data['labels'].append(current_date.strftime('%Y-%m-%d'))
            chart_data['revenue'].append(revenue_dict.get(str(current_date), 0))
            current_date += timedelta(days=1)
        
        return jsonify(chart_data), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get revenue trends'}), 500

#------Lot Performance,revenue distribution,bookings distribution----------------#
@analytics_bp.route('/admin/lot-performance', methods=['GET'])
@admin_required
@cache_admin_data(timeout=1200)  # Cache for 20 minutes - performance data
@monitor_performance
def lot_performance():
    try:
        lot_stats = db.session.query(
            Lot.name,
            func.count(ReserveSpot.id).label('total_bookings'),
            func.sum(ReserveSpot.cost).label('total_revenue'),
            func.count(func.distinct(ReserveSpot.user_id)).label('unique_users')
        ).join(
            Spot, Lot.id == Spot.lot_id
        ).join(
            ReserveSpot, Spot.id == ReserveSpot.spot_id
        ).filter(
            ReserveSpot.cost.isnot(None)
        ).group_by(Lot.id, Lot.name).all()
        
        chart_data = {
            'labels': [stat.name for stat in lot_stats],
            'bookings': [stat.total_bookings for stat in lot_stats],
            'revenue': [float(stat.total_revenue or 0) for stat in lot_stats],
            'unique_users': [stat.unique_users for stat in lot_stats]
        }
        
        return jsonify(chart_data), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get lot performance'}), 500

#---------------Hourly Trends---------------------------#
@analytics_bp.route('/admin/occupancy-trends', methods=['GET'])
@admin_required
@cache_admin_data(timeout=1800)  # Cache for 30 minutes - trending data
@monitor_performance
def occupancy_trends():
    try:
        # Get bookings with hour of day
        hourly_bookings = db.session.query(
            extract('hour', ReserveSpot.parking_time).label('hour'),
            func.count(ReserveSpot.id).label('booking_count')
        ).group_by(extract('hour', ReserveSpot.parking_time)).all()
        
        # Initialize 24-hour array
        hourly_data = [0] * 24
        for booking in hourly_bookings:
            hourly_data[int(booking.hour)] = booking.booking_count
        
        chart_data = {
            'labels': [f'{i:02d}:00' for i in range(24)],
            'bookings': hourly_data
        }
        
        return jsonify(chart_data), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get occupancy trends'}), 500

#------------------------------------------------------#
#------------------User Charts-------------------------#
#------------------------------------------------------#

#--------------User Stats (Topbar),Month Summary---------#
@analytics_bp.route('/user/spending-overview', methods=['GET'])
@login_required
@cache_user_data(timeout=600)  # Cache for 10 minutes - user overview
@monitor_performance
def user_spending_overview():
    try:
        user_id = g.current_user.id
        
        # Total spent
        total_spent = db.session.query(func.sum(ReserveSpot.cost)).filter(
            and_(ReserveSpot.user_id == user_id, ReserveSpot.cost.isnot(None))
        ).scalar() or 0
        
        # Total bookings
        total_bookings = ReserveSpot.query.filter_by(user_id=user_id).count()
        
        # Active bookings
        active_bookings = ReserveSpot.query.filter_by(
            user_id=user_id, leaving_time=None
        ).count()
        
        # Average cost per booking
        avg_cost = total_spent / total_bookings if total_bookings > 0 else 0
        
        # Favorite lot (most booked)
        favorite_lot = db.session.query(
            Lot.name,
            func.count(ReserveSpot.id).label('booking_count')
        ).join(
            Spot, Lot.id == Spot.lot_id
        ).join(
            ReserveSpot, Spot.id == ReserveSpot.spot_id
        ).filter(
            ReserveSpot.user_id == user_id
        ).group_by(Lot.id, Lot.name).order_by(
            func.count(ReserveSpot.id).desc()
        ).first()
        
        return jsonify({
            'total_spent': round(total_spent, 2),
            'total_bookings': total_bookings,
            'active_bookings': active_bookings,
            'avg_cost_per_booking': round(avg_cost, 2),
            'favorite_lot': favorite_lot.name if favorite_lot else None
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get user spending overview'}), 500

#------------------Your Spending Trends--------------------#
@analytics_bp.route('/user/spending-trends', methods=['GET'])
@login_required
@cache_user_data(timeout=900)  # Cache for 15 minutes - trending data
@monitor_performance
def user_spending_trends():
    try:
        user_id = g.current_user.id
        
        # Get date range from query params (default to last 30 days)
        days = int(request.args.get('days', 30))
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)
        
        # Get spending by date
        spending_by_date = db.session.query(
            func.date(ReserveSpot.parking_time).label('date'),
            func.sum(ReserveSpot.cost).label('spending')
        ).filter(
            and_(
                ReserveSpot.user_id == user_id,
                ReserveSpot.parking_time >= start_date,
                ReserveSpot.parking_time <= end_date,
                ReserveSpot.cost.isnot(None)
            )
        ).group_by(func.date(ReserveSpot.parking_time)).all()
        
        # Format data for charts
        chart_data = {
            'labels': [],
            'spending': []
        }
        
        # Create a dict for easy lookup
        spending_dict = {str(item.date): float(item.spending) for item in spending_by_date}
        
        # Fill in all dates in range (including zeros)
        current_date = start_date.date()
        while current_date <= end_date.date():
            chart_data['labels'].append(current_date.strftime('%Y-%m-%d'))
            chart_data['spending'].append(spending_dict.get(str(current_date), 0))
            current_date += timedelta(days=1)
        
        return jsonify(chart_data), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get user spending trends'}), 500

#-----Your Parking Lot Usage,Booking distribution,Revenue distribution----------#
@analytics_bp.route('/user/lot-usage', methods=['GET'])
@login_required
def user_lot_usage():
    try:
        user_id = g.current_user.id
        
        lot_usage = db.session.query(
            Lot.name,
            func.count(ReserveSpot.id).label('booking_count'),
            func.sum(ReserveSpot.cost).label('total_spent')
        ).join(
            Spot, Lot.id == Spot.lot_id
        ).join(
            ReserveSpot, Spot.id == ReserveSpot.spot_id
        ).filter(
            ReserveSpot.user_id == user_id
        ).group_by(Lot.id, Lot.name).all()
        
        chart_data = {
            'labels': [usage.name for usage in lot_usage],
            'bookings': [usage.booking_count for usage in lot_usage],
            'spending': [float(usage.total_spent or 0) for usage in lot_usage]
        }
        
        return jsonify(chart_data), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get user lot usage'}), 500
