from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from inventory_system.db.models import db, User
import os

profile_bp = Blueprint('profile', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@profile_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        # 1. Update Username
        new_username = request.form.get('username')
        if new_username and new_username != current_user.username:
            existing_user = User.query.filter_by(username=new_username).first()
            if existing_user:
                flash('Username already taken.', 'danger')
            else:
                current_user.username = new_username
                flash('Username updated successfully.', 'success')

        # 2. Update Password
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if new_password:
            if not current_password:
                flash('Please provide your current password to change it.', 'danger')
            elif not check_password_hash(current_user.password_hash, current_password):
                 flash('Incorrect current password.', 'danger')
            elif new_password != confirm_password:
                flash('New passwords do not match.', 'danger')
            else:
                current_user.password_hash = generate_password_hash(new_password)
                flash('Password updated successfully.', 'success')

        # 3. Update Theme
        theme = request.form.get('theme')
        if theme:
            current_user.theme_preference = theme
            # No flash needed, visual change is enough or can add one

        # 4. Update Profile Picture
        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(f"user_{current_user.id}_{file.filename}")
                
                # Ensure upload folder exists
                upload_folder = os.path.join(current_app.static_folder, 'uploads', 'avatars')
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)
                
                file.save(os.path.join(upload_folder, filename))
                
                # Save relative path to DB
                current_user.profile_image = f"uploads/avatars/{filename}"
                flash('Profile picture updated.', 'success')

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating profile: {str(e)}', 'danger')
        
        return redirect(url_for('profile.profile'))

    return render_template('profile.html')
