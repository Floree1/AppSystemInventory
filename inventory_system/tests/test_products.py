from inventory_system.db.models import Product

def test_product_list_requires_login(client):
    response = client.get('/products/', follow_redirects=True)
    assert b'Login' in response.data

def test_admin_can_create_product(client, app, auth):
    auth.login(username='admin', password='password')
    
    response = client.post('/products/add', data={
        'name': 'Test Product',
        'sku': 'TEST-001',
        'quantity': 10,
        'min_stock': 5,
        'buy_price': 100,
        'sell_price': 150,
        'description': 'A test product'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Product added successfully!' in response.data
    
    with app.app_context():
        product = Product.query.filter_by(sku='TEST-001').first()
        assert product is not None
        assert product.name == 'Test Product'

def test_employee_cannot_delete_product(client, app, auth):
    # First create a product as admin
    auth.login(username='admin', password='password')
    client.post('/products/add', data={
        'name': 'To Delete',
        'sku': 'DEL-001',
        'quantity': 5
    })
    auth.logout()

    # Login as employee
    auth.login(username='employee', password='password')
    
    with app.app_context():
        product = Product.query.filter_by(sku='DEL-001').first()
        product_id = product.id

    # Try to delete
    response = client.post(f'/products/delete/{product_id}', follow_redirects=True)
    
    # Assert
    # We expect a 403 Forbidden or a redirected user with a flash message.
    # The @admin_required decorator usually returns 403.
    # Let's check if it redirected (302) or is 403.
    # In `auth/decorators.py` (not shown but typical), it likely aborts with 403.
    
    if response.status_code == 403:
        assert True
    elif response.status_code == 200:
        # Maybe it redirected to a 'Permission Denied' page or back to dashboard
        assert b'Product deleted' not in response.data
    else:
        # Redirect
        assert response.status_code == 302
    
    # Verify product still exists in DB
    with app.app_context():
        product = Product.query.get(product_id)
        assert product is not None
