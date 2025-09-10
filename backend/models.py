from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from extensions import db

class User(db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    fullname = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.Enum('user', 'admin', name='role'), default='user')
    
    # Relationships
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

class Lot(db.Model):
    __tablename__ = 'lot'
    
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    prime_location_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    pincode = db.Column(db.Integer, nullable=False)
    no_of_spots = db.Column(db.Integer, nullable=False)
    
    # Relationships
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

class Spot(db.Model):
    __tablename__ = 'spot'
    
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey("lot.id", ondelete="CASCADE"))
    spot_number = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum('A', 'O', name='status'), default='A')  # A=Available, O=Occupied
    
    # Relationships
    lot = db.relationship('Lot', back_populates='spots')
    reserved_spots = db.relationship('ReserveSpot', back_populates='spot', cascade="all, delete-orphan", passive_deletes=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'lot_id': self.lot_id,
            'spot_number': self.spot_number,
            'status': self.status
        }

class ReserveSpot(db.Model):
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
