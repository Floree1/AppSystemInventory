from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from inventory_system.db.models import db, Provider, Log
from inventory_system.auth.decorators import admin_required

providers_bp = Blueprint('providers', __name__, url_prefix='/providers')

@providers_bp.route('/')
@login_required
def list_providers():
    providers = Provider.query.all()
    return render_template('providers/list.html', providers=providers)

@providers_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_provider():
    if request.method == 'POST':
        name = request.form.get('name')
        contact_person = request.form.get('contact_person')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        
        new_provider = Provider(name=name, contact_person=contact_person, email=email, phone=phone, address=address)
        db.session.add(new_provider)
        db.session.commit()
        
        # Log action
        log = Log(user_id=current_user.id, action='Add Provider', details=f'Added provider {name}')
        db.session.add(log)
        db.session.commit()
        
        flash('Provider added successfully!', 'success')
        return redirect(url_for('providers.list_providers'))
    
    return render_template('providers/form.html', action='Add')

@providers_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_provider(id):
    provider = Provider.query.get_or_404(id)
    
    if request.method == 'POST':
        provider.name = request.form.get('name')
        provider.contact_person = request.form.get('contact_person')
        provider.email = request.form.get('email')
        provider.phone = request.form.get('phone')
        provider.address = request.form.get('address')
        
        db.session.commit()
        
        # Log action
        log = Log(user_id=current_user.id, action='Edit Provider', details=f'Edited provider {provider.name} (ID: {id})')
        db.session.add(log)
        db.session.commit()
        
        flash('Provider updated successfully!', 'success')
        return redirect(url_for('providers.list_providers'))
    
    return render_template('providers/form.html', provider=provider, action='Edit')

@providers_bp.route('/delete/<int:id>', methods=['POST'])
@admin_required
def delete_provider(id):
    provider = Provider.query.get_or_404(id)
    db.session.delete(provider)
    db.session.commit()
    
    # Log action
    log = Log(user_id=current_user.id, action='Delete Provider', details=f'Deleted provider {provider.name} (ID: {id})')
    db.session.add(log)
    db.session.commit()
    
    flash('Provider deleted successfully!', 'success')
    return redirect(url_for('providers.list_providers'))
