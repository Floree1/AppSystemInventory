from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from inventory_system.db.models import db, Product, Category, Provider
from inventory_system.app.audit import AuditLogger
from inventory_system.auth.decorators import admin_required
from datetime import datetime

products_bp = Blueprint('products', __name__, url_prefix='/products')

@products_bp.route('/')
@login_required
def list_products():
    search = request.args.get('search')
    if search:
        products = Product.query.filter(
            (Product.name.contains(search)) | 
            (Product.sku.contains(search))
        ).all()
    else:
        products = Product.query.all()
    return render_template('products/list.html', products=products)

@products_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'POST':
        name = request.form.get('name')
        sku = request.form.get('sku')
        category_id = request.form.get('category_id')
        provider_id = request.form.get('provider_id')
        quantity = request.form.get('quantity', 0)
        min_stock = request.form.get('min_stock', 5)
        buy_price = request.form.get('buy_price', 0.0)
        sell_price = request.form.get('sell_price', 0.0)
        description = request.form.get('description')

        existing_product = Product.query.filter_by(sku=sku).first()
        if existing_product:
            flash('Product with this SKU already exists.', 'danger')
            return redirect(url_for('products.add_product'))

        new_product = Product(
            name=name, sku=sku, category_id=category_id, provider_id=provider_id,
            quantity=quantity, min_stock=min_stock, buy_price=buy_price,
            sell_price=sell_price, description=description
        )
        db.session.add(new_product)
        db.session.commit()
        
        # Log action
        AuditLogger.log(action='Add Product', details=f'Added product {name} (SKU: {sku})')
        
        flash('Product added successfully!', 'success')
        return redirect(url_for('products.list_products'))

    categories = Category.query.all()
    providers = Provider.query.all()
    return render_template('products/form.html', categories=categories, providers=providers, action='Add')

@products_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    product = Product.query.get_or_404(id)
    
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.sku = request.form.get('sku')
        product.category_id = request.form.get('category_id')
        product.provider_id = request.form.get('provider_id')
        product.min_stock = request.form.get('min_stock')
        product.buy_price = request.form.get('buy_price')
        product.sell_price = request.form.get('sell_price')
        product.description = request.form.get('description')
        
        db.session.commit()
        
        # Log action
        AuditLogger.log(action='Edit Product', details=f'Edited product {product.name} (ID: {id})')
        
        flash('Product updated successfully!', 'success')
        return redirect(url_for('products.list_products'))

    categories = Category.query.all()
    providers = Provider.query.all()
    return render_template('products/form.html', product=product, categories=categories, providers=providers, action='Edit')

@products_bp.route('/delete/<int:id>', methods=['POST'])
@admin_required
def delete_product(id):
    product = Product.query.get_or_404(id)
    product_name = product.name # Capture name before deletion
    
    db.session.delete(product)
    db.session.commit()
    
    # Log action
    AuditLogger.log(action='Delete Product', details=f'Deleted product {product_name} (ID: {id})')
    
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('products.list_products'))
