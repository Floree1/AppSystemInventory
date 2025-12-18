from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from inventory_system.db.models import db, User
from inventory_system.app.audit import AuditLogger
from inventory_system.auth.decorators import admin_required
from werkzeug.security import generate_password_hash

users_bp = Blueprint('users', __name__, url_prefix='/users')

@users_bp.route('/')
@admin_required
def list_users():
    users = User.query.all()
    return render_template('users/list.html', users=users)

@users_bp.route('/add', methods=['GET', 'POST'])
@admin_required
def add_user():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return redirect(url_for('users.add_user'))
            
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password_hash=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()
        
        # Log action
        AuditLogger.log(action='Add User', details=f'Added user {username} as {role}')
        
        flash('User added successfully!', 'success')
        return redirect(url_for('users.list_users'))
        
    return render_template('users/form.html', action='Add')

@users_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_user(id):
    user = User.query.get_or_404(id)
    
    if request.method == 'POST':
        user.username = request.form.get('username')
        user.role = request.form.get('role')
        
        password = request.form.get('password')
        if password:
            user.password_hash = generate_password_hash(password)
            
        db.session.commit()
        
        # Log action
        AuditLogger.log(action='Edit User', details=f'Edited user {user.username} (ID: {id})')
        
        flash('User updated successfully!', 'success')
        return redirect(url_for('users.list_users'))
        
    return render_template('users/form.html', user=user, action='Edit')

@users_bp.route('/delete/<int:id>', methods=['POST'])
@admin_required
def delete_user(id):
    if id == current_user.id:
        flash('You cannot delete yourself.', 'danger')
        return redirect(url_for('users.list_users'))
        
    user = User.query.get_or_404(id)
    user_name = user.username
    
    db.session.delete(user)
    db.session.commit()
    
    # Log action
    AuditLogger.log(action='Delete User', details=f'Deleted user {user_name} (ID: {id})')
    
    flash('User deleted successfully!', 'success')
    return redirect(url_for('users.list_users'))
