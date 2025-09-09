import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix
from datetime import datetime, date
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "fire-dept-secret-key-2024")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///fire_dept.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Import models after db initialization
with app.app_context():
    import models
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return models.User.query.get(int(user_id))

# ===== ROUTES =====

@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form.get('role', 'applicant')
        
        # Check if user already exists
        if models.User.query.filter_by(username=username).first():
            flash('Username already exists!', 'danger')
            return redirect(url_for('register'))
        
        if models.User.query.filter_by(email=email).first():
            flash('Email already registered!', 'danger')
            return redirect(url_for('register'))
        
        # Create new user
        user = models.User(username=username, email=email, role=role)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = models.User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash(f'Welcome {user.username}!', 'success')
            
            # Redirect based on role
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid username or password!', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def user_dashboard():
    """Applicant dashboard showing their applications"""
    if current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))
    
    applications = models.Application.query.filter_by(applicant_id=current_user.id).order_by(models.Application.created_at.desc()).all()
    return render_template('user_dashboard.html', applications=applications)

@app.route('/submit_application', methods=['GET', 'POST'])
@login_required
def submit_application():
    """Submit new application"""
    if current_user.role != 'applicant':
        flash('Access denied!', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        app_type = request.form['type']
        description = request.form['description']
        business_name = request.form['business_name']
        business_address = request.form['business_address']
        contact_phone = request.form['contact_phone']
        
        # Create new application
        application = models.Application(
            applicant_id=current_user.id,
            type=app_type,
            description=description,
            business_name=business_name,
            business_address=business_address,
            contact_phone=contact_phone
        )
        
        db.session.add(application)
        db.session.commit()
        
        flash('Application submitted successfully!', 'success')
        return redirect(url_for('user_dashboard'))
    
    return render_template('submit_application.html')

@app.route('/application/<int:app_id>')
@login_required
def view_application(app_id):
    """View detailed application status"""
    application = models.Application.query.get_or_404(app_id)
    
    # Check permission
    if current_user.role != 'admin' and application.applicant_id != current_user.id:
        flash('Access denied!', 'danger')
        return redirect(url_for('index'))
    
    # Get related data
    inspections = models.Inspection.query.filter_by(application_id=app_id).all()
    noc = models.NOC.query.filter_by(application_id=app_id).first()
    
    return render_template('view_application.html', 
                         application=application, 
                         inspections=inspections, 
                         noc=noc)

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    """Admin dashboard showing all applications"""
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('user_dashboard'))
    
    applications = models.Application.query.order_by(models.Application.created_at.desc()).all()
    return render_template('admin_dashboard.html', applications=applications)

@app.route('/admin/update_status/<int:app_id>', methods=['POST'])
@login_required
def update_application_status(app_id):
    """Update application status (admin only)"""
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('user_dashboard'))
    
    application = models.Application.query.get_or_404(app_id)
    new_status = request.form['status']
    
    application.status = new_status
    application.updated_at = datetime.utcnow()
    db.session.commit()
    
    flash(f'Application status updated to {new_status}!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/inspections')
@login_required
def manage_inspections():
    """Manage inspections (admin only)"""
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('user_dashboard'))
    
    inspections = models.Inspection.query.join(models.Application).order_by(models.Inspection.created_at.desc()).all()
    applications = models.Application.query.filter(models.Application.type.in_(['inspection', 'noc'])).all()
    
    return render_template('inspections.html', inspections=inspections, applications=applications)

@app.route('/admin/schedule_inspection', methods=['POST'])
@login_required
def schedule_inspection():
    """Schedule new inspection"""
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('manage_inspections'))
    
    application_id = request.form['application_id']
    date_str = request.form['date']
    time = request.form['time']
    inspector_name = request.form['inspector_name']
    
    # Parse date
    inspection_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    
    # Create inspection
    inspection = models.Inspection(
        application_id=application_id,
        date=inspection_date,
        time=time,
        inspector_name=inspector_name
    )
    
    # Update application status
    application = models.Application.query.get(application_id)
    application.status = 'inspection_scheduled'
    application.updated_at = datetime.utcnow()
    
    db.session.add(inspection)
    db.session.commit()
    
    flash('Inspection scheduled successfully!', 'success')
    return redirect(url_for('manage_inspections'))

@app.route('/admin/nocs')
@login_required
def manage_nocs():
    """Manage NOCs (admin only)"""
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('user_dashboard'))
    
    nocs = models.NOC.query.join(models.Application).order_by(models.NOC.issue_date.desc()).all()
    applications = models.Application.query.filter_by(type='noc').filter_by(status='approved').all()
    
    return render_template('nocs.html', nocs=nocs, applications=applications)

@app.route('/admin/issue_noc', methods=['POST'])
@login_required
def issue_noc():
    """Issue NOC certificate"""
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('manage_nocs'))
    
    application_id = request.form['application_id']
    remarks = request.form.get('remarks', '')
    
    # Generate NOC number
    noc_count = models.NOC.query.count() + 1
    noc_number = f"NOC-{datetime.now().year}-{noc_count:04d}"
    
    # Create NOC
    noc = models.NOC(
        application_id=application_id,
        issue_date=date.today(),
        status='issued',
        remarks=remarks,
        noc_number=noc_number
    )
    
    # Update application status
    application = models.Application.query.get(application_id)
    application.status = 'approved'
    application.updated_at = datetime.utcnow()
    
    db.session.add(noc)
    db.session.commit()
    
    flash(f'NOC {noc_number} issued successfully!', 'success')
    return redirect(url_for('manage_nocs'))
