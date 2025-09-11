from flask import Blueprint, jsonify, g, request
from models import db, User, ReserveSpot, Lot, Spot
from extensions import cache
from decorators import login_required
from datetime import datetime, timezone
from sqlalchemy import and_

user_bp = Blueprint('user', __name__, url_prefix='/api/user')

def ensure_timezone_aware(dt):
    """Ensure datetime is timezone-aware. If naive, assume UTC."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt

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

# ================ PARKING LOT DISCOVERY ================

@user_bp.route('/lots', methods=['GET'])
@login_required
def get_available_lots():
    """Get all parking lots with availability information"""
    try:
        lots = Lot.query.all()
        lots_data = []
        
        for lot in lots:
            # Count available spots
            available_spots = Spot.query.filter_by(
                lot_id=lot.id, 
                status='A'
            ).count()
            
            lot_info = lot.to_dict()
            lot_info['available_spots'] = available_spots
            lot_info['is_available'] = available_spots > 0
            
            lots_data.append(lot_info)
        
        return jsonify({
            'lots': lots_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get parking lots'}), 500

@user_bp.route('/lots/<int:lot_id>/spots', methods=['GET'])
@login_required
def get_lot_spots(lot_id):
    """Get available spots for a specific lot"""
    try:
        lot = Lot.query.get_or_404(lot_id)
        
        available_spots = Spot.query.filter_by(
            lot_id=lot_id, 
            status='A'
        ).all()
        
        return jsonify({
            'lot': lot.to_dict(),
            'available_spots': [spot.to_dict() for spot in available_spots]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get lot spots'}), 500

# ================ PARKING SPOT BOOKING ================

@user_bp.route('/book-spot', methods=['POST'])
@login_required
def book_parking_spot():
    """Book a parking spot with auto-allocation"""
    try:
        data = request.get_json()
        lot_id = data.get('lot_id')
        vehicle_number = data.get('vehicle_number')
        
        if not lot_id or not vehicle_number:
            return jsonify({'error': 'Lot ID and vehicle number are required'}), 400
        
        # Check if user already has an active reservation (no leaving_time means active)
        active_reservation = ReserveSpot.query.filter_by(
            user_id=g.current_user.id,
            leaving_time=None
        ).first()
        
        if active_reservation:
            return jsonify({'error': 'You already have an active parking reservation'}), 400
        
        # Find an available spot in the lot (auto-allocation)
        available_spot = Spot.query.filter_by(
            lot_id=lot_id,
            status='A'
        ).first()
        
        if not available_spot:
            return jsonify({'error': 'No available spots in this parking lot'}), 400
        
        # Get lot information for pricing
        lot = Lot.query.get(lot_id)
        
        # Create reservation
        reservation = ReserveSpot(
            user_id=g.current_user.id,
            spot_id=available_spot.id,
            vehicle_no=vehicle_number,
            parking_time=datetime.now(timezone.utc),
            cost=lot.price,  # Initial cost based on hourly rate
            location=lot.name  # Use lot name as location
        )
        
        # Mark spot as occupied
        available_spot.status = 'O'
        
        db.session.add(reservation)
        db.session.commit()
        
        return jsonify({
            'message': 'Parking spot booked successfully',
            'reservation': {
                'id': reservation.id,
                'spot_number': available_spot.spot_number,
                'lot_name': lot.name,
                'vehicle_number': vehicle_number,
                'parking_time': reservation.parking_time.isoformat(),
                'hourly_rate': lot.price
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to book parking spot'}), 500

@user_bp.route('/release-spot/<int:reservation_id>', methods=['POST'])
@login_required
def release_parking_spot(reservation_id):
    """Release a parking spot and calculate final cost"""
    try:
        # Get the reservation
        reservation = ReserveSpot.query.filter_by(
            id=reservation_id,
            user_id=g.current_user.id,
            leaving_time=None  # Active reservation has no leaving_time
        ).first()
        
        if not reservation:
            return jsonify({'error': 'Active reservation not found'}), 404
        
        # Calculate parking duration and cost
        now = datetime.now(timezone.utc)
        
        # Handle timezone-aware and timezone-naive parking_time
        parking_time = ensure_timezone_aware(reservation.parking_time)
        
        duration_hours = (now - parking_time).total_seconds() / 3600
        
        # Get lot for pricing (need to get lot through spot relationship)
        spot = Spot.query.get(reservation.spot_id)
        lot = spot.lot
        final_cost = max(duration_hours * lot.price, lot.price)  # Minimum 1 hour charge
        
        # Update reservation
        reservation.leaving_time = now
        reservation.cost = final_cost
        
        # Mark spot as available
        spot.status = 'A'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Parking spot released successfully',
            'duration_hours': round(duration_hours, 2),
            'final_cost': round(final_cost, 2)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to release parking spot: {str(e)}'}), 500

# ================ BOOKING MANAGEMENT ================

@user_bp.route('/reservations', methods=['GET'])
@login_required
def get_user_reservations():
    """Get all reservations for the current user"""
    try:
        reservations = ReserveSpot.query.filter_by(
            user_id=g.current_user.id
        ).order_by(ReserveSpot.parking_time.desc()).all()
        
        reservations_data = []
        for reservation in reservations:
            # Get lot through spot relationship
            spot = Spot.query.get(reservation.spot_id)
            lot = spot.lot
            
            reservation_info = {
                'id': reservation.id,
                'lot_name': lot.name,
                'lot_location': lot.prime_location_name,
                'spot_number': spot.spot_number,
                'vehicle_number': reservation.vehicle_no,
                'parking_time': reservation.parking_time.isoformat(),
                'leaving_time': reservation.leaving_time.isoformat() if reservation.leaving_time else None,
                'cost': reservation.cost,
                'status': 'released' if reservation.leaving_time else 'active',
                'duration_hours': None
            }
            
            # Calculate duration if completed
            if reservation.leaving_time:
                leaving_time = ensure_timezone_aware(reservation.leaving_time)
                parking_time = ensure_timezone_aware(reservation.parking_time)
                duration = (leaving_time - parking_time).total_seconds() / 3600
                reservation_info['duration_hours'] = round(duration, 2)
            
            reservations_data.append(reservation_info)
        
        return jsonify({
            'reservations': reservations_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get reservations'}), 500

@user_bp.route('/current-reservation', methods=['GET'])
@login_required
def get_current_reservation():
    """Get the current active reservation for the user"""
    try:
        reservation = ReserveSpot.query.filter_by(
            user_id=g.current_user.id,
            leaving_time=None  # Active reservation has no leaving_time
        ).first()
        
        if not reservation:
            return jsonify({'current_reservation': None}), 200
        
        # Get lot through spot relationship
        spot = Spot.query.get(reservation.spot_id)
        lot = spot.lot
        
        # Calculate current duration and estimated cost
        now = datetime.now(timezone.utc)
        
        # Handle timezone-aware and timezone-naive parking_time
        parking_time = ensure_timezone_aware(reservation.parking_time)
        
        current_duration = (now - parking_time).total_seconds() / 3600
        estimated_cost = max(current_duration * lot.price, lot.price)
        
        reservation_info = {
            'id': reservation.id,
            'lot_name': lot.name,
            'lot_location': lot.prime_location_name,
            'spot_number': spot.spot_number,
            'vehicle_number': reservation.vehicle_no,
            'parking_time': reservation.parking_time.isoformat(),
            'current_duration_hours': round(current_duration, 2),
            'estimated_cost': round(estimated_cost, 2),
            'hourly_rate': lot.price
        }
        
        return jsonify({
            'current_reservation': reservation_info
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get current reservation'}), 500
