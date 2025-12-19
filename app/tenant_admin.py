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
                # Save only the filename for portability
                tenants[new_access_code] = db_filename
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

@tenant_admin_bp.route('/delete_tenant/<access_code>', methods=['POST'])
def delete_tenant(access_code):
    password = request.form.get('password')
    if password != Config.TENANT_ADMIN_PASSWORD:
        flash('Incorrect Master Password. Action aborted.', 'danger')
        return redirect(url_for('tenant_admin.manage_tenants'))

    try:
        with open(Config.TENANTS_FILE, 'r') as f:
            tenants = json.load(f)
        
        if access_code not in tenants:
            flash('Tenant not found.', 'danger')
            return redirect(url_for('tenant_admin.manage_tenants'))

        db_entry = tenants[access_code]
        
        # Resolve path
        if db_entry.startswith('sqlite:///'):
            db_path_part = db_entry.split('///')[1]
            db_path = os.path.abspath(db_path_part)
        else:
            db_path = os.path.join(Config.BASE_DIR, 'tenants', db_entry)

        # Delete DB file
        if os.path.exists(db_path):
            try:
                os.remove(db_path)
                print(f"Deleted DB file: {db_path}")
            except Exception as e:
                print(f"Error deleting file {db_path}: {e}")
                # We continue to remove from JSON even if file delete fails (maybe it's already gone)

        # Remove from JSON
        del tenants[access_code]
        
        with open(Config.TENANTS_FILE, 'w') as f:
            json.dump(tenants, f, indent=4)

        flash(f'Tenant {access_code} has been deleted.', 'success')

    except Exception as e:
        flash(f'An error occurred: {e}', 'danger')

    return redirect(url_for('tenant_admin.manage_tenants'))

@tenant_admin_bp.route('/reset_tenant/<access_code>', methods=['POST'])
def reset_tenant(access_code):
    password = request.form.get('password')
    if password != Config.TENANT_ADMIN_PASSWORD:
        flash('Incorrect Master Password. Action aborted.', 'danger')
        return redirect(url_for('tenant_admin.manage_tenants'))

    try:
        with open(Config.TENANTS_FILE, 'r') as f:
            tenants = json.load(f)
        
        if access_code not in tenants:
            flash('Tenant not found.', 'danger')
            return redirect(url_for('tenant_admin.manage_tenants'))

        db_entry = tenants[access_code]
        
        # Resolve path
        if db_entry.startswith('sqlite:///'):
            db_uri = db_entry
            db_path_part = db_entry.split('///')[1]
            db_path = os.path.abspath(db_path_part)
        else:
            db_path = os.path.join(Config.BASE_DIR, 'tenants', db_entry)
            db_uri = f'sqlite:///{db_path}'

        # Delete existing DB file to ensure clean slate
        if os.path.exists(db_path):
            try:
                os.remove(db_path)
            except Exception as e:
                flash(f'Error clearing old database: {e}', 'warning')

        # Re-create database
        if create_tenant_db(db_uri):
            flash(f'Tenant {access_code} has been reset to default state.', 'success')
        else:
            flash(f'Failed to reset tenant {access_code}.', 'danger')

    except Exception as e:
        flash(f'An error occurred: {e}', 'danger')

    return redirect(url_for('tenant_admin.manage_tenants'))
