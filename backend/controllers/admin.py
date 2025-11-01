#==============================================================================
#                           ADMIN CONTROLLER
#                         Administrative Dashboard & Management
#==============================================================================
# Author: Student
# Description: Admin-only API endpoints for managing the parking system
# Features: User management, lot management, analytics, cache monitoring
# Access: Admin role required for all endpoints
#==============================================================================

from flask import Blueprint, jsonify, g, request
from models import db, User, Lot, Spot, ReserveSpot
from extensions import cache
from decorators import login_required, admin_required
from datetime import datetime, timezone
from cache_strategy import (
    cache_admin_data, CacheKeys, CacheInvalidator, 
    invalidate_cache_on_change, monitor_performance, CacheConfig,
    AdvancedCacheManager
)

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

#-------------------------------------------------------#
#-------------------Admin stats at topbar---------------#
#-------------------------------------------------------#
@admin_bp.route('/dashboard-stats', methods=['GET'])
@admin_required
@cache_admin_data(timeout=CacheConfig.ADMIN_DASHBOARD)
@monitor_performance
def get_admin_dashboard_stats():
    try:
        # Get basic counts
        total_users = User.query.filter_by(role='user').count()
        total_lots = Lot.query.count()
        total_spots = Spot.query.count()
        
        # Get revenue
        total_revenue = db.session.query(db.func.sum(ReserveSpot.cost)).scalar() or 0
        
        # Get additional stats for better insights
        active_reservations = ReserveSpot.query.filter_by(leaving_time=None).count()
        occupied_spots = Spot.query.filter_by(status='O').count()
        occupancy_rate = round((occupied_spots / max(total_spots, 1)) * 100, 2)
        
        return jsonify({
            'total_users': total_users,
            'total_lots': total_lots,
            'total_spots': total_spots,
            'total_revenue': total_revenue,
            'active_reservations': active_reservations,
            'occupied_spots': occupied_spots,
            'occupancy_rate': occupancy_rate
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get admin stats'}), 500

#-------------------------------------------------------#
#------------Parking lot management section-------------#
#-------------------------------------------------------#

#------Get all parking lots with their spot statistics------#
@admin_bp.route('/lots', methods=['GET'])
@admin_required
def get_all_lots():
    try:
        # Query database directly (no caching for now)
        lots = Lot.query.all()
        lots_data = []
        
        for lot in lots:
            lot_dict = lot.to_dict()
            # Add additional admin-specific data
            total_spots = Spot.query.filter_by(lot_id=lot.id).count()
            occupied_spots = Spot.query.filter_by(lot_id=lot.id, status='O').count()
            available_spots = total_spots - occupied_spots
            
            lot_dict.update({
                'total_spots': total_spots,
                'occupied_spots': occupied_spots,
                'available_spots': available_spots,
                'occupancy_rate': round((occupied_spots / max(total_spots, 1)) * 100, 2)
            })
            lots_data.append(lot_dict)
        
        return jsonify({'lots': lots_data}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get parking lots'}), 500

#------Create a new parking lot and automatically generate spots------#

@admin_bp.route('/lots', methods=['POST'])
@admin_required
@monitor_performance
def create_lot():
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

#-------------------------------------------------------#
#------------Edit and Delete Parking Lots---------------#
#-------------------------------------------------------#

#-------Get detailed info about a specific lot------#
@admin_bp.route('/lots/<int:lot_id>', methods=['GET'])
@admin_required
def get_lot_details(lot_id):
    try:
        lot = Lot.query.get_or_404(lot_id)
        return jsonify({
            'lot': lot.to_dict(),
            'spots': [spot.to_dict() for spot in lot.spots]
        }), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get lot details'}), 500

#---------Edit a parking lot---------#
@admin_bp.route('/lots/<int:lot_id>', methods=['PUT'])
@admin_required
@monitor_performance
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

#---------Delete a parking lot---------#

@admin_bp.route('/lots/<int:lot_id>', methods=['DELETE'])
@admin_required
@monitor_performance
def delete_lot(lot_id):
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

#---------------------------------------------------------------------------#
#-------------------------Cache Management Routes--------------------------#
#---------------------------------------------------------------------------#

@admin_bp.route('/cache/stats', methods=['GET'])
@admin_required
@monitor_performance
def get_cache_stats():
    """Get comprehensive cache statistics"""
    try:
        cache_manager = AdvancedCacheManager()
        stats = cache_manager.get_cache_stats()
        cache_size = cache_manager.get_cache_size()
        
        combined_stats = {**stats, **cache_size}
        
        return jsonify({
            'cache_stats': combined_stats,
            'message': 'Cache statistics retrieved successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get cache statistics'}), 500

@admin_bp.route('/cache/warm-up', methods=['POST'])
@admin_required
@monitor_performance
def warm_up_cache():
    """Manually trigger cache warm-up"""
    try:
        cache_manager = AdvancedCacheManager()
        cache_manager.warm_up_cache()
        
        return jsonify({
            'message': 'Cache warm-up completed successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to warm up cache'}), 500

@admin_bp.route('/cache/clear', methods=['POST'])
@admin_required
@monitor_performance
def clear_cache():
    """Clear all application cache"""
    try:
        cache_manager = AdvancedCacheManager()
        success = cache_manager.clear_all_cache()
        
        if success:
            return jsonify({
                'message': 'All cache cleared successfully'
            }), 200
        else:
            return jsonify({'error': 'Failed to clear cache'}), 500
            
    except Exception as e:
        return jsonify({'error': 'Failed to clear cache'}), 500

@admin_bp.route('/cache/health', methods=['GET'])
@admin_required
def cache_health_check():
    """Check cache health and connectivity"""
    try:
        import redis
        from extensions import cache as app_cache
        
        test_key = "health_check_test"
        test_value = {"status": "ok", "timestamp": datetime.now().isoformat()}
        
        # Test write
        app_cache.set(test_key, test_value, timeout=60)
        
        # Test read  
        retrieved = app_cache.get(test_key)
        
        if retrieved and retrieved.get('status') == 'ok':
            return jsonify({
                "status": "healthy", 
                "cache_type": str(type(app_cache.cache)),
                "test_successful": True
            }), 200
        else:
            return jsonify({
                "status": "unhealthy", 
                "error": "Cache read/write failed"
            }), 500
                
    except Exception as e:
        return jsonify({
            "status": "error", 
            "error": str(e)
        }), 500

#-------------------------------------------------------#
#----------------Spot Status Monitoring-----------------#
#-------------------------------------------------------#

@admin_bp.route('/spots/status', methods=['GET'])
@admin_required
def get_spots_status():
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
                reservation = ReserveSpot.query.filter_by(
                    spot_id=spot.id,
                    leaving_time=None  # Active reservation
                ).first()
                
                if reservation:
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
        return jsonify({'error': f'Failed to get spot status: {str(e)}'}), 500

