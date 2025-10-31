#==============================================================================
#                           ONLYPARK DATABASE MODELS
#                         Data Structure & Relationships
#==============================================================================
# Description: Database models for users, parking lots, spots, and reservations
# Features: SQLAlchemy ORM, password hashing, relationships with cascading deletes
# Purpose: Defines how our data is stored and connected in the database
#==============================================================================

from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from extensions import db

#=============================== USER MODEL ==================================#

class User(db.Model):
    """
    User Model - Stores user account information
    This handles both regular users and admins
    """
    __tablename__ = 'user'
    
    # Basic user info
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)  # Login email
    fullname = db.Column(db.String(100), nullable=False)  # User's full name
    password = db.Column(db.String(128), nullable=False)  # Hashed password
    role = db.Column(db.Enum('user', 'admin', name='role'), default='user')  # user or admin
    
    # Relationships - connects to user's reservations
    reserved_spots = db.relationship('ReserveSpot', back_populates='user', cascade="all, delete-orphan", passive_deletes=True)
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'fullname': self.fullname,
            'role': self.role
        }

#============================== PARKING LOT MODEL =============================#

class Lot(db.Model):
    """
    Parking Lot Model - Stores information about parking locations
    Each lot has multiple parking spots
    """
    __tablename__ = 'lot'
    
    # Lot basic info
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)  # Lot name like "Mall Parking"
    prime_location_name = db.Column(db.String(100), nullable=False)  # Area name
    price = db.Column(db.Float, nullable=False)  # Hourly parking rate
    pincode = db.Column(db.Integer, nullable=False)  # Location pincode
    no_of_spots = db.Column(db.Integer, nullable=False)  # Total parking spots
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # When lot was added
    
    # Relationships - connects to all spots in this lot
    spots = db.relationship('Spot', back_populates='lot', cascade="all, delete-orphan", passive_deletes=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'prime_location_name': self.prime_location_name,
            'price': self.price,
            'pincode': self.pincode,
            'no_of_spots': self.no_of_spots,
            'available_spots': len([s for s in self.spots if s.status == 'A']),
            'occupied_spots': len([s for s in self.spots if s.status == 'O'])
        }

#============================= PARKING SPOT MODEL =============================#

class Spot(db.Model):
    """
    Parking Spot Model - Individual parking spaces within a lot
    Each spot can be Available (A) or Occupied (O)
    """
    __tablename__ = 'spot'
    
    # Spot info
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey("lot.id", ondelete="CASCADE"))  # Which lot this spot belongs to
    spot_number = db.Column(db.Integer, nullable=False)  # Spot number like 1, 2, 3...
    status = db.Column(db.Enum('A', 'O', name='status'), default='A')  # A=Available, O=Occupied
    
    # Relationships - connects to lot and reservations
    lot = db.relationship('Lot', back_populates='spots')
    reserved_spots = db.relationship('ReserveSpot', back_populates='spot', cascade="all, delete-orphan", passive_deletes=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'lot_id': self.lot_id,
            'spot_number': self.spot_number,
            'status': self.status
        }

#=========================== RESERVATION MODEL =============================#

class ReserveSpot(db.Model):
    """
    Reservation Model - Stores booking information when users reserve spots
    Links users to specific parking spots with timing details
    """
    __tablename__ = 'reserve_spot'
    
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey("spot.id", ondelete="CASCADE"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"))
    vehicle_no = db.Column(db.String(20), nullable=False)
    parking_time = db.Column(db.DateTime, nullable=False)
    leaving_time = db.Column(db.DateTime, nullable=True)
    cost = db.Column(db.Float, nullable=True, default=0)
    location = db.Column(db.String(100), nullable=False)
    
    # Relationships
    spot = db.relationship('Spot', back_populates='reserved_spots')
    user = db.relationship('User', back_populates='reserved_spots')
    
    def to_dict(self):
        return {
            'id': self.id,
            'spot_id': self.spot_id,
            'user_id': self.user_id,
            'vehicle_no': self.vehicle_no,
            'parking_time': self.parking_time.isoformat() if self.parking_time else None,
            'leaving_time': self.leaving_time.isoformat() if self.leaving_time else None,
            'cost': self.cost,
            'location': self.location,
            'status': 'released' if self.leaving_time else 'parked'
        }
