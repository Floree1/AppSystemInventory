from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from inventory_system.config import Config
from flask_login import login_required, current_user
from inventory_system.db.models import db, Product, Provider, User, StockMovement, Log, Category
from inventory_system.auth.decorators import admin_required
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/language/<language>')
def set_language(language=None):
    if language in Config.LANGUAGES:
        session['locale'] = language
    return redirect(request.referrer or url_for('main.dashboard'))

@main_bp.route('/')
@login_required
def dashboard():
    total_products = Product.query.count()
    total_providers = Provider.query.count()
    movements_today = StockMovement.query.filter(db.func.date(StockMovement.timestamp) == db.func.date(datetime.now())).count()
    low_stock_products = Product.query.filter(Product.quantity <= Product.min_stock).count()
    recent_movements = StockMovement.query.order_by(StockMovement.timestamp.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                           total_products=total_products,
                           total_providers=total_providers,
                           movements_today=movements_today,
                           low_stock_items=low_stock_products,
                           recent_movements=recent_movements)

# Placeholder routes for other sections
@main_bp.route('/products')
@login_required
def products():
    products = Product.query.all()
    return render_template('products/list.html', products=products)

@main_bp.route('/providers')
@login_required
def providers():
    providers = Provider.query.all()
    return render_template('providers/list.html', providers=providers)

@main_bp.route('/movements')
@login_required
def movements():
    movements = StockMovement.query.order_by(StockMovement.timestamp.desc()).all()
    return render_template('movements/list.html', movements=movements)

@main_bp.route('/users')
@admin_required
def users():
    users = User.query.all()
    return render_template('users/list.html', users=users)

@main_bp.route('/logs')
@admin_required
def logs():
    # Filters
    action_filter = request.args.get('action')
    user_filter = request.args.get('user_id')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    query = Log.query
    
    if action_filter:
        query = query.filter(Log.action.contains(action_filter))
    
    if user_filter:
        query = query.filter(Log.user_id == user_filter)
        
    if date_from:
        try:
            dt_from = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(Log.timestamp >= dt_from)
        except ValueError:
            pass # Ignore invalid date
            
    if date_to:
        try:
            dt_to = datetime.strptime(date_to, '%Y-%m-%d')
            # Add one day to include the end date fully
            dt_to = dt_to.replace(hour=23, minute=59, second=59)
            query = query.filter(Log.timestamp <= dt_to)
        except ValueError:
            pass
            
    # Pagination
    page = request.args.get('page', 1, type=int)
    logs_pagination = query.order_by(Log.timestamp.desc()).paginate(page=page, per_page=20)
    
    # Data for filters
    users = User.query.all()
    # Get unique actions for dropdown - simplified approach
    # distinct() might vary by DB, but works for basic SQLite use cases usually
    # or just let user type it. For now, let's just pass users.
    
    return render_template('logs/list.html', logs=logs_pagination, users=users)

@main_bp.route('/reports')
@login_required
def reports():
    return render_template('reports/index.html')
