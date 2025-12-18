from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from inventory_system.db.models import db, Product, StockMovement
from inventory_system.app.audit import AuditLogger
from datetime import datetime

movements_bp = Blueprint('movements', __name__, url_prefix='/movements')

@movements_bp.route('/')
@login_required
def list_movements():
    movements = StockMovement.query.order_by(StockMovement.timestamp.desc()).all()
    return render_template('movements/list.html', movements=movements)

@movements_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_movement():
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        movement_type = request.form.get('movement_type')
        quantity = int(request.form.get('quantity'))
        reason = request.form.get('reason')
        
        product = Product.query.get_or_404(product_id)
        
        if movement_type == 'OUT' and product.quantity < quantity:
            flash(f'Insufficient stock! Current stock: {product.quantity}', 'danger')
            return redirect(url_for('movements.add_movement'))
            
        # Update product quantity
        if movement_type == 'IN':
            product.quantity += quantity
        else:
            product.quantity -= quantity
            
        # Create movement record
        movement = StockMovement(
            product_id=product_id,
            user_id=current_user.id,
            movement_type=movement_type,
            quantity=quantity,
            reason=reason
        )
        
        db.session.add(movement)
        db.session.commit()
        
        # Log action
        AuditLogger.log(action='Stock Movement', details=f'{movement_type} {quantity} of {product.name} (Reason: {reason})')
        
        flash('Stock movement recorded successfully!', 'success')
        return redirect(url_for('movements.list_movements'))
        
    products = Product.query.all()
    return render_template('movements/form.html', products=products)
