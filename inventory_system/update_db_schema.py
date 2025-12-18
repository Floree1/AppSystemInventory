import sqlite3
import os

def add_columns_to_users():
    # Path to the database file
    # We need to find all tenant databases + the main one if it exists (though main one might be different)
    # Based on previous file exploration, there is a 'database.db' in 'inventory_system' and tenant dbs in 'inventory_system/tenants'
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # List of databases to update
    dbs_to_update = []
    
    # 1. Main database (if used)
    main_db = os.path.join(base_dir, 'database.db')
    if os.path.exists(main_db):
        dbs_to_update.append(main_db)
        
    # 2. Tenant databases
    tenants_dir = os.path.join(base_dir, 'tenants')
    if os.path.exists(tenants_dir):
        for filename in os.listdir(tenants_dir):
            if filename.endswith(".db"):
                dbs_to_update.append(os.path.join(tenants_dir, filename))
                
    print(f"Found {len(dbs_to_update)} databases to update.")
    
    for db_path in dbs_to_update:
        print(f"Updating {db_path}...")
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if columns exist
            cursor.execute("PRAGMA table_info(users)")
            columns = [info[1] for info in cursor.fetchall()]
            
            if 'profile_image' not in columns:
                print("  - Adding column 'profile_image'...")
                cursor.execute("ALTER TABLE users ADD COLUMN profile_image TEXT")
            else:
                print("  - Column 'profile_image' already exists.")
                
            if 'theme_preference' not in columns:
                print("  - Adding column 'theme_preference'...")
                cursor.execute("ALTER TABLE users ADD COLUMN theme_preference TEXT DEFAULT 'default'")
            else:
                print("  - Column 'theme_preference' already exists.")
                
            conn.commit()
            conn.close()
            print("  - Done.")
            
        except Exception as e:
            print(f"  - Error updating {db_path}: {e}")

if __name__ == "__main__":
    add_columns_to_users()
