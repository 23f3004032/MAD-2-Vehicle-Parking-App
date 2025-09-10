from flask import Flask
from flask_cors import CORS
from sqlalchemy import event
from sqlalchemy.engine import Engine
import sqlite3
import os
from config import Config
from extensions import db, mail, cache, jwt
from celery_app import make_celery

# Enable cascading deletes in SQLite
@event.listens_for(Engine, "connect")
def enable_sqlite_fk(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config.from_object(Config)
    
    # CORS for frontend
    CORS(app, origins=["http://localhost:5173"], supports_credentials=True)
    
    # Initialize extensions
    db.init_app(app)
    cache.init_app(app)
    mail.init_app(app)
    jwt.init_app(app)
    
    # Initialize Celery
    make_celery(app)
    
    # Create export directory
    os.makedirs(app.config['EXPORT_DIR'], exist_ok=True)
    
    # Import and register blueprints
    from controllers import blueprints
    for bp in blueprints:
        app.register_blueprint(bp)
    
    return app

app = create_app()

@app.route('/')
def index():
    return {
        'message': 'Vehicle Parking App API',
        'version': '1.0',
        'status': 'running'
    }

@app.route('/health')
def health():
    return {'status': 'healthy', 'database': 'connected'}

def create_admin():
    """Create default admin user if not exists"""
    from models import User
    try:
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            admin = User(
                email='admin@onlypark.com',
                fullname='Admin',
                role='admin'
            )
            admin.set_password('admin')
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin user created: admin@onlypark.com / admin")
        else:
            print("✅ Admin user already exists")
    except Exception as e:
        print(f"❌ Error creating admin: {e}")
        db.session.rollback()

if __name__ == '__main__':
    with app.app_context():
        # Import models to register them with SQLAlchemy
        import models
        
        # Create all tables
        db.create_all()
        print("🚀 Database tables created successfully!")
        
        # Create default admin
        create_admin()
        print("🚀 Database initialized successfully!")
    
    # Run the application
    app.run(debug=True, host='0.0.0.0', port=5000)
