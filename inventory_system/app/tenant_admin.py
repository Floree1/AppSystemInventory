from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from werkzeug.security import check_password_hash, generate_password_hash
from inventory_system.config import Config
from inventory_system.db.models import db, User
import json
import os
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

tenant_admin_bp = Blueprint('tenant_admin', __name__)

def create_tenant_db(db_uri):
    """Creates a new database and initializes its schema and a default admin user."""
    try:
        engine = create_engine(db_uri)
        # Create all tables
        db.metadata.create_all(engine)
        
        # Create a session to add the admin user
        TempSession = sessionmaker(bind=engine)
        temp_session = TempSession()
        
        # Create a default admin user for the new tenant
        if not temp_session.query(User).filter_by(username='admin').first():
            hashed_password = generate_password_hash('password')
            admin = User(username='admin', password_hash=hashed_password, role='admin')
            temp_session.add(admin)
            temp_session.commit()
            print(f"Admin user created for database at {db_uri}")
            
        temp_session.close()
        return True
    except Exception as e:
        print(f"Error creating tenant database: {e}")
        return False

@tenant_admin_bp.route('/manage-tenants', methods=['GET', 'POST'])
def manage_tenants():
    if request.method == 'POST':
        password = request.form.get('password')
        
        # Check against the master password from config
        if password != Config.TENANT_ADMIN_PASSWORD:
            flash('Incorrect password.', 'danger')
            return redirect(url_for('tenant_admin.manage_tenants'))

        # --- Create New Tenant Logic ---
        # Generate a new unique access code
        new_access_code = str(uuid.uuid4().hex)[:8].upper()
        
        # Define the new database path
        db_filename = f"tenant_{new_access_code}.db"
        db_path = os.path.join(Config.BASE_DIR, 'tenants', db_filename)
        db_uri = f'sqlite:///{db_path}'

        # Create the new database and admin user
        if not create_tenant_db(db_uri):
            flash('Failed to create new tenant database.', 'danger')
            return redirect(url_for('tenant_admin.manage_tenants'))

        # Update tenants.json
        try:
            with open(Config.TENANTS_FILE, 'r+') as f:
                tenants = json.load(f)
                tenants[new_access_code] = db_uri
                f.seek(0)
                json.dump(tenants, f, indent=4)
                f.truncate()
            flash(f'Successfully created new tenant! Access Code: {new_access_code}', 'success')
        except Exception as e:
            flash(f'Error updating tenants file: {e}', 'danger')

        return redirect(url_for('tenant_admin.manage_tenants'))

    # For GET request, just show the management page
    try:
        with open(Config.TENANTS_FILE) as f:
            current_tenants = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        current_tenants = {}
        
    return render_template('tenant_admin/manage.html', tenants=current_tenants)
