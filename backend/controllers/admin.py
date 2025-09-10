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

# ================ PARKING LOT MANAGEMENT CRUD ================

@admin_bp.route('/lots', methods=['GET'])
@admin_required
def get_all_lots():
    """Get all parking lots with their spot statistics"""
    try:
        lots = Lot.query.all()
        return jsonify({
            'lots': [lot.to_dict() for lot in lots]
        }), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get parking lots'}), 500

@admin_bp.route('/lots', methods=['POST'])
@admin_required
def create_lot():
    """Create a new parking lot and automatically generate spots"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'prime_location_name', 'price', 'pincode', 'no_of_spots']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if lot name already exists
        existing_lot = Lot.query.filter_by(name=data['name']).first()
        if existing_lot:
            return jsonify({'error': 'Parking lot with this name already exists'}), 400
        
        # Create new lot
        lot = Lot(
            name=data['name'],
            prime_location_name=data['prime_location_name'],
            price=float(data['price']),
            pincode=int(data['pincode']),
            no_of_spots=int(data['no_of_spots'])
        )
        
        db.session.add(lot)
        db.session.flush()  # Get the lot.id before creating spots
        
        # Automatically create spots for the lot
        for spot_num in range(1, int(data['no_of_spots']) + 1):
            spot = Spot(
                lot_id=lot.id,
                spot_number=spot_num,
                status='A'  # Available by default
            )
            db.session.add(spot)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Parking lot created successfully',
            'lot': lot.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create parking lot'}), 500

@admin_bp.route('/lots/<int:lot_id>', methods=['GET'])
@admin_required
def get_lot_details(lot_id):
    """Get detailed information about a specific lot"""
    try:
        lot = Lot.query.get_or_404(lot_id)
        return jsonify({
            'lot': lot.to_dict(),
            'spots': [spot.to_dict() for spot in lot.spots]
        }), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get lot details'}), 500

@admin_bp.route('/lots/<int:lot_id>', methods=['PUT'])
@admin_required
def update_lot(lot_id):
    """Update parking lot information"""
    try:
        lot = Lot.query.get_or_404(lot_id)
        data = request.get_json()
        
        # Update fields if provided
        if 'name' in data:
            # Check if new name conflicts with existing lot
            existing_lot = Lot.query.filter(Lot.name == data['name'], Lot.id != lot_id).first()
            if existing_lot:
                return jsonify({'error': 'Parking lot with this name already exists'}), 400
            lot.name = data['name']
        
        if 'prime_location_name' in data:
            lot.prime_location_name = data['prime_location_name']
        if 'price' in data:
            lot.price = float(data['price'])
        if 'pincode' in data:
            lot.pincode = int(data['pincode'])
        
        # Handle spot count changes
        if 'no_of_spots' in data:
            new_spot_count = int(data['no_of_spots'])
            current_spot_count = len(lot.spots)
            
            if new_spot_count > current_spot_count:
                # Add new spots
                for spot_num in range(current_spot_count + 1, new_spot_count + 1):
                    spot = Spot(
                        lot_id=lot.id,
                        spot_number=spot_num,
                        status='A'
                    )
                    db.session.add(spot)
            elif new_spot_count < current_spot_count:
                # Remove excess spots (only if they're available)
                spots_to_remove = Spot.query.filter(
                    Spot.lot_id == lot_id,
                    Spot.spot_number > new_spot_count,
                    Spot.status == 'A'
                ).all()
                
                occupied_spots = Spot.query.filter(
                    Spot.lot_id == lot_id,
                    Spot.spot_number > new_spot_count,
                    Spot.status == 'O'
                ).count()
                
                if occupied_spots > 0:
                    return jsonify({'error': f'Cannot reduce spots. {occupied_spots} spots are currently occupied'}), 400
                
                for spot in spots_to_remove:
                    db.session.delete(spot)
            
            lot.no_of_spots = new_spot_count
        
        db.session.commit()
        
        return jsonify({
            'message': 'Parking lot updated successfully',
            'lot': lot.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update parking lot'}), 500

@admin_bp.route('/lots/<int:lot_id>', methods=['DELETE'])
@admin_required
def delete_lot(lot_id):
    """Delete a parking lot and all its spots"""
    try:
        lot = Lot.query.get_or_404(lot_id)
        
        # Check if any spots are currently occupied
        occupied_spots = Spot.query.filter_by(lot_id=lot_id, status='O').count()
        if occupied_spots > 0:
            return jsonify({'error': f'Cannot delete lot. {occupied_spots} spots are currently occupied'}), 400
        
        # Delete the lot (cascade will handle spots and reservations)
        db.session.delete(lot)
        db.session.commit()
        
        return jsonify({'message': 'Parking lot deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete parking lot'}), 500

# ================ SPOT STATUS MONITORING ================

@admin_bp.route('/spots/status', methods=['GET'])
@admin_required
def get_spots_status():
    """Get comprehensive status of all parking spots across all lots"""
    try:
        # Query spots with their lots and active reservations
        spots = db.session.query(Spot, Lot).join(Lot, Spot.lot_id == Lot.id).all()
        
        spots_data = []
        for spot, lot in spots:
            spot_info = {
                'spot_id': spot.id,
                'lot_id': spot.lot_id,
                'lot_name': lot.name,
                'spot_number': spot.spot_number,
                'status': spot.status,
                'location': lot.prime_location_name or 'Unknown Location'
            }
            
            # If spot is occupied, get reservation details
            if spot.status == 'O':
                # Find active reservation for this spot
                reservation = ReserveSpot.query.filter_by(
                    spot_id=spot.id,
                    leaving_time=None  # Active reservation
                ).first()
                
                if reservation:
                    # Get user details
                    user = User.query.get(reservation.user_id)
                    spot_info.update({
                        'vehicle_number': reservation.vehicle_no,
                        'user_name': user.fullname if user else 'Unknown User',
                        'user_email': user.email if user else 'Unknown',
                        'parking_time': reservation.parking_time.isoformat(),
                        'reservation_id': reservation.id
                    })
                else:
                    # Spot marked as occupied but no active reservation found
                    spot_info.update({
                        'vehicle_number': 'N/A',
                        'user_name': 'No active reservation',
                        'user_email': 'N/A',
                        'parking_time': None,
                        'reservation_id': None
                    })
            
            spots_data.append(spot_info)
        
        # Calculate summary statistics
        total_spots = len(spots_data)
        occupied_spots = len([s for s in spots_data if s['status'] == 'O'])
        available_spots = total_spots - occupied_spots
        occupancy_rate = round((occupied_spots / total_spots * 100) if total_spots > 0 else 0, 1)
        
        summary = {
            'total_spots': total_spots,
            'available_spots': available_spots,
            'occupied_spots': occupied_spots,
            'occupancy_rate': occupancy_rate
        }
        
        return jsonify({
            'spots': spots_data,
            'summary': summary
        }), 200
        
    except Exception as e:
        print(f"Error in get_spots_status: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to get spot status: {str(e)}'}), 500

@admin_bp.route('/test', methods=['GET'])
@admin_required  
def test_admin_api():
    """Simple test endpoint to verify admin API is working"""
    return jsonify({'message': 'Admin API is working', 'user': g.current_user.email}), 200
