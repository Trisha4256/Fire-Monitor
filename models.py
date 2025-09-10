from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    """User model for authentication - supports both applicants and admins"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    role = db.Column(db.String(20), nullable=False, default='applicant')  # 'applicant' or 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to applications
    applications = db.relationship('Application', backref='applicant', lazy=True)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)

class Application(db.Model):
    """Application model for fire department requests"""
    id = db.Column(db.Integer, primary_key=True)
    applicant_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(100), nullable=False)  # 'inspection', 'noc', 'license_renewal'
    description = db.Column(db.Text, nullable=False)
    business_name = db.Column(db.String(200))
    business_address = db.Column(db.Text)
    contact_phone = db.Column(db.String(20))
    image_filename = db.Column(db.String(255))  # Store uploaded image filename
    status = db.Column(db.String(50), nullable=False, default='pending')  # 'pending', 'inspection_scheduled', 'approved', 'rejected'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    inspections = db.relationship('Inspection', backref='application', lazy=True)
    noc = db.relationship('NOC', backref='application', uselist=False)

class Inspection(db.Model):
    """Inspection model for tracking fire safety inspections"""
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('application.id'), nullable=False)
    date = db.Column(db.Date)
    time = db.Column(db.String(10))
    inspector_name = db.Column(db.String(100))
    status = db.Column(db.String(50), default='scheduled')  # 'scheduled', 'completed', 'failed'
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class NOC(db.Model):
    """No Objection Certificate model"""
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('application.id'), nullable=False)
    issue_date = db.Column(db.Date)
    expiry_date = db.Column(db.Date)
    status = db.Column(db.String(50), default='pending')  # 'pending', 'issued', 'expired'
    remarks = db.Column(db.Text)
    noc_number = db.Column(db.String(50), unique=True)
