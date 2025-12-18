from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from inventory_system.db.models import User, db, Log
from werkzeug.security import check_password_hash
from inventory_system.config import Config
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        access_code = request.form.get('access_code')

        try:
            with open(current_app.config['TENANTS_FILE']) as f:
                tenants = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            flash('System configuration error. Please contact admin.', 'danger')
            return render_template('login.html')

        if access_code not in tenants:
            flash('Invalid Access Code.', 'danger')
            return render_template('login.html')

        db_entry = tenants[access_code]
        
        # logic to handle both absolute URI and relative filename
        if db_entry.startswith('sqlite:///'):
            # It's explicitly an absolute URI (or relative URI)
            db_uri = db_entry
        else:
            # It's assumed to be a filename in the 'tenants' directory
            # Construct the absolute path for the current environment
            db_path = os.path.join(current_app.config['BASE_DIR'], 'tenants', db_entry)
            db_uri = f'sqlite:///{db_path}'
        
        # Create a temporary engine and session to check credentials for this tenant
        try:
            engine = create_engine(db_uri)
            TempSession = sessionmaker(bind=engine)
            temp_session = TempSession()
            user = temp_session.query(User).filter_by(username=username).first()
            
            if user and check_password_hash(user.password_hash, password):
                login_user(user)
                session['db_uri'] = db_uri
                session['access_code'] = access_code

                # Log login to the tenant's database
                log = Log(user_id=user.id, action='Login', details=f'User {username} logged in.', timestamp=datetime.now())
                temp_session.add(log)
                temp_session.commit()
                
                temp_session.close()
                
                next_page = request.args.get('next')
                return redirect(next_page or url_for('main.dashboard'))
            else:
                temp_session.close()
                flash('Login Unsuccessful. Please check credentials.', 'danger')

        except Exception as e:
            flash(f'Database connection error: {e}', 'danger')
            if 'temp_session' in locals() and temp_session:
                temp_session.close()
            
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    # The `db.session` will be pointing to the correct tenant DB
    # thanks to the upcoming @before_request handler.
    try:
        log = Log(user_id=current_user.id, action='Logout', details='User logged out', timestamp=datetime.now())
        db.session.add(log)
        db.session.commit()
    except Exception:
        # If the session commit fails for any reason, we should still log the user out.
        db.session.rollback()

    logout_user()
    # Clear tenant info from session
    session.pop('db_uri', None)
    session.pop('access_code', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

