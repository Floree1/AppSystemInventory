import pytest
import os
import sys
import json
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from inventory_system.app import create_app, db
from inventory_system.config import Config
from inventory_system.db.models import User
from werkzeug.security import generate_password_hash

# Create a temporary directory for the test run
TEST_DIR = tempfile.mkdtemp()
TEST_DB_PATH = os.path.join(TEST_DIR, 'test_tenant.db')
TEST_TENANTS_FILE = os.path.join(TEST_DIR, 'test_tenants.json')
TEST_ACCESS_CODE = 'TEST1234'

class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    TENANTS_FILE = TEST_TENANTS_FILE
    BABEL_DEFAULT_LOCALE = 'en'
    # Start with the test DB as default
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{TEST_DB_PATH}'

@pytest.fixture(scope='session', autouse=True)
def setup_test_environment():
    """Sets up the test database and tenants file once for the session"""
    
    # 1. Create the Test DB
    engine = create_engine(f'sqlite:///{TEST_DB_PATH}')
    
    # We need to manually create the tables because we are outside the app context initially
    # or we can use the app to do it.
    # Let's use a minimal app setup just to create tables.
    _app = create_app(TestConfig)
    with _app.app_context():
        db.create_all()
        
        # Create Admin if not exists (create_app might have created it)
        if not User.query.filter_by(username='admin').first():
            hashed_password = generate_password_hash('password')
            admin = User(username='admin', password_hash=hashed_password, role='admin')
            db.session.add(admin)
        
        # Create Employee
        if not User.query.filter_by(username='employee').first():
            hashed_password_emp = generate_password_hash('password')
            employee = User(username='employee', password_hash=hashed_password_emp, role='employee')
            db.session.add(employee)
        
        db.session.commit()
    
    # 2. Create tenants.json
    tenants_data = {TEST_ACCESS_CODE: f'sqlite:///{TEST_DB_PATH}'}
    with open(TEST_TENANTS_FILE, 'w') as f:
        json.dump(tenants_data, f)
        
    yield
    
    # Cleanup (Optional, passing for now to avoid permission errors on windows)
    pass

@pytest.fixture
def app():
    app = create_app(TestConfig)
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def auth(client):
    return AuthActions(client)

class AuthActions:
    def __init__(self, client):
        self._client = client

    def login(self, username='admin', password='password', access_code=TEST_ACCESS_CODE):
        return self._client.post(
            '/login',
            data={
                'username': username, 
                'password': password,
                'access_code': access_code
            },
            follow_redirects=True
        )

    def logout(self):
        return self._client.get('/logout', follow_redirects=True)
