# create_initial_tenants.py

import os
import sys
import json
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash

# Add the project directory to the Python path to allow importing from the app
project_path = os.path.abspath(os.path.dirname(__file__))
# Assumes the script is in 'inventory_system', and 'inventory_system' is the root package dir
sys.path.insert(0, os.path.dirname(project_path)) 


# Now we can import from the application
# We need to define the db object and User model structure here again
# to avoid complex app context setup in a standalone script.
# A better way would be to structure the project to make models easily importable.
from inventory_system.db.models import db, User
from inventory_system.config import Config


def create_tenant_db_and_admin(db_uri):
    """Creates a new database, its schema, and a default admin user."""
    try:
        engine = create_engine(db_uri)
        # Reflects the models' schema and creates tables
        db.metadata.create_all(engine)
        
        TempSession = sessionmaker(bind=engine)
        temp_session = TempSession()
        
        if not temp_session.query(User).filter_by(username='admin').first():
            hashed_password = generate_password_hash('password')
            admin = User(username='admin', password_hash=hashed_password, role='admin')
            temp_session.add(admin)
            temp_session.commit()
            print(f"  - Admin user created.")
        else:
            print(f"  - Admin user already exists.")

        if not temp_session.query(User).filter_by(username='user').first():
            hashed_password = generate_password_hash('password')
            employee = User(username='user', password_hash=hashed_password, role='employee')
            temp_session.add(employee)
            temp_session.commit()
            print(f"  - Employee user created.")
        else:
            print(f"  - Employee user already exists.")
            
        temp_session.close()
        return True
    except Exception as e:
        print(f"  - Error creating database/admin: {e}")
        return False

def main():
    print("--- Starting Initial Tenant Setup ---")
    
    if not os.path.exists(os.path.join(Config.BASE_DIR, 'tenants')):
        os.makedirs(os.path.join(Config.BASE_DIR, 'tenants'))
        print(f"Created tenants directory.")

    tenants_data = {}
    num_tenants = 10
    
    for i in range(num_tenants):
        access_code = str(uuid.uuid4().hex)[:8].upper()
        print(f"\nProcessing Tenant {i+1}/{num_tenants} (Code: {access_code})")
        
        db_filename = f"tenant_{access_code}.db"
        db_path = os.path.join(Config.BASE_DIR, 'tenants', db_filename)
        db_uri = f'sqlite:///{db_path}'
        
        if create_tenant_db_and_admin(db_uri):
            # Save only the filename to ensure portability across environments (Windows/Linux)
            # The app will reconstruct the full path at runtime.
            tenants_data[access_code] = db_filename
            print(f"  - Successfully created database: {db_filename}")
        else:
            print(f"  - FAILED to create database for code {access_code}")

    try:
        with open(Config.TENANTS_FILE, 'w') as f:
            json.dump(tenants_data, f, indent=4)
        print(f"\nSuccessfully wrote {len(tenants_data)} tenant configurations to {Config.TENANTS_FILE}")
    except Exception as e:
        print(f"\nError writing to tenants file: {e}")
        
    print("\n--- Tenant Setup Complete ---")
    print("You can now run the main application.")
    print("Generated Access Codes:")
    for code in tenants_data.keys():
        print(f"- {code}")

if __name__ == '__main__':
    # This script is intended to be run from the 'inventory_system' directory.
    # e.g., python create_initial_tenants.py
    main()
