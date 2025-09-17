from flask import Blueprint, jsonify, g, request
from models import db, User, ReserveSpot, Lot, Spot
from extensions import cache
from decorators import login_required
from datetime import datetime, timezone
from sqlalchemy import and_
from tasks import export_user_data_csv

user_bp = Blueprint('user', __name__, url_prefix='/api/user')

#---------------------------------------------------------------------------#
#-------------Helper Function to handle timezone and billings---------------#
#---------------------------------------------------------------------------#
def ensure_timezone_aware(dt):
    """Ensure datetime is timezone-aware. If naive, assume UTC."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt

#---------------------------------------------------------------------------#
#-------------Frontend Route to show logged in user details----------------#
#---------------------------------------------------------------------------#
@user_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    try:
        return jsonify({
            'user': g.current_user.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get profile'}), 500

#---------------------------------------------------------------------------#
#------------- User Dashboard Details at top bar when logged in-------------#
#---------------------------------------------------------------------------#
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
        
        total_spent = sum(r.cost or 0 for r in completed_reservations) # Handle None costs added this for fallback
        
        return jsonify({
            'total_reservations': total_reservations,
            'active_reservations': active_reservations,
            'total_spent': total_spent,
            'completed_reservations': len(completed_reservations)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get dashboard stats'}), 500

#---------------------------------------------------------------------------#
#------------- Get all parking lots with availability information-----------#
#---------------------------------------------------------------------------#
@user_bp.route('/lots', methods=['GET'])
@login_required
def get_available_lots():
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

#---------------------------------------------------------------------------#
#-------------------------------Book spot-----------------------------------#
#---------------------------------------------------------------------------#

@user_bp.route('/book-spot', methods=['POST'])
@login_required
def book_parking_spot():
    try:
        data = request.get_json()
        lot_id = data.get('lot_id')
        vehicle_number = data.get('vehicle_number')
        
        if not lot_id or not vehicle_number:
            return jsonify({'error': 'Lot ID and vehicle number are required'}), 400
        
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

#---------------------------------------------------------------------------#
#------------------------Release Spot-------------------------------------#
#---------------------------------------------------------------------------#

@user_bp.route('/release-spot/<int:reservation_id>', methods=['POST'])
@login_required
def release_parking_spot(reservation_id):
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
        parking_time = ensure_timezone_aware(reservation.parking_time)
        duration_hours = (now - parking_time).total_seconds() / 3600
        
        # Get lot for pricing (need to get lot through spot relationship)
        spot = Spot.query.get(reservation.spot_id)
        lot = spot.lot
        final_cost = duration_hours * lot.price
        
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

#---------------------------------------------------------------------------#
#-----------------------Past Bookings---------------------------------------#
#---------------------------------------------------------------------------#

@user_bp.route('/reservations', methods=['GET'])
@login_required
def get_user_reservations():
    try:
        reservations = ReserveSpot.query.filter(
            ReserveSpot.user_id == g.current_user.id,
            ReserveSpot.leaving_time.isnot(None)  # Only completed reservations
        ).order_by(ReserveSpot.parking_time.desc()).all()
        
        reservations_data = []
        for reservation in reservations:
            # Get lot through spot relationship
            spot = Spot.query.get(reservation.spot_id)
            lot = spot.lot
            
            # Calculate duration for completed reservations
            leaving_time = ensure_timezone_aware(reservation.leaving_time)
            parking_time = ensure_timezone_aware(reservation.parking_time)
            duration = (leaving_time - parking_time).total_seconds() / 3600
            
            reservation_info = {
                'id': reservation.id,
                'lot_name': lot.name,
                'lot_location': lot.prime_location_name,
                'spot_number': spot.spot_number,
                'vehicle_number': reservation.vehicle_no,
                'parking_time': reservation.parking_time.isoformat(),
                'leaving_time': reservation.leaving_time.isoformat(),
                'cost': reservation.cost,
                'status': 'completed',  # All are completed since we filtered for leaving_time
                'duration_hours': round(duration, 2)
            }
            
            reservations_data.append(reservation_info)
        
        return jsonify({
            'reservations': reservations_data,
            'count': len(reservations_data)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get reservations'}), 500

#---------------------------------------------------------------------------#
#---------------------Active Bookings---------------------------------------#
#---------------------------------------------------------------------------#

@user_bp.route('/active-bookings', methods=['GET'])
@login_required
def get_active_bookings():
    try:
        reservations = ReserveSpot.query.filter_by(
            user_id=g.current_user.id,
            leaving_time=None  # Active reservations have no leaving_time
        ).all()
        
        active_reservations = []
        now = datetime.now(timezone.utc)
        
        for reservation in reservations:
            # Get lot through spot relationship
            spot = Spot.query.get(reservation.spot_id)
            lot = spot.lot
            
            # Calculate current duration and estimated cost
            parking_time = ensure_timezone_aware(reservation.parking_time)
            current_duration = (now - parking_time).total_seconds() / 3600
            estimated_cost = current_duration * lot.price
            
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
            
            active_reservations.append(reservation_info)
        
        return jsonify({
            'active_reservations': active_reservations,
            'count': len(active_reservations)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get active reservations'}), 500

#---------------------------------------------------------------------------#
#-------------CSV Export Endpoint - Trigger async CSV generation-----------#
#---------------------------------------------------------------------------#
@user_bp.route('/export-data', methods=['POST'])
@login_required
def export_user_data():
    """Trigger CSV export for the current user"""
    try:
        user_id = g.current_user.id
        
        # Get export type from request (optional)
        data = request.get_json()
        export_type = data.get('export_type', 'all') if data else 'all'
        
        # Make sure the task is properly imported
        from tasks import export_user_data_csv
        
        # Trigger the Celery task
        task = export_user_data_csv.delay(user_id, export_type)
        
        print(f"Export task initiated for user {user_id}, task_id: {task.id}")  # Add logging
        
        return jsonify({
            'message': 'Data export initiated successfully',
            'task_id': task.id,
            'status': 'processing',
            'email': g.current_user.email,
            'info': 'You will receive an email with your data export shortly'
        }), 202  # 202 Accepted - request has been accepted for processing
        
    except Exception as e:
        print(f"Export error: {str(e)}")  # Add logging
        return jsonify({'error': f'Failed to initiate export: {str(e)}'}), 500

#---------------------------------------------------------------------------#
#-------------Check Export Status - Check Celery task status---------------#
#---------------------------------------------------------------------------#
@user_bp.route('/export-status/<task_id>', methods=['GET'])
@login_required
def check_export_status(task_id):
    """Check the status of a CSV export task"""
    try:
        from celery_app import celery
        
        task = celery.AsyncResult(task_id)
        
        if task.state == 'PENDING':
            response = {
                'status': 'pending',
                'message': 'Export is being processed...'
            }
        elif task.state == 'SUCCESS':
            response = {
                'status': 'completed',
                'message': 'Export completed successfully',
                'result': task.result
            }
        elif task.state == 'FAILURE':
            response = {
                'status': 'failed',
                'message': 'Export failed',
                'error': str(task.info)
            }
        else:
            response = {
                'status': task.state,
                'message': f'Export status: {task.state}'
            }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to check export status: {str(e)}'}), 500
