import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # This is now a fallback URI. The actual URI will be set per-request.
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    LANGUAGES = ['en', 'es', 'pt']
    BABEL_DEFAULT_LOCALE = 'es'

    # --- Multi-tenancy configuration ---
    # The file that maps access codes to database URIs
    TENANTS_FILE = os.path.join(BASE_DIR, 'tenants.json')
    
    # The password to access the tenant management page
    TENANT_ADMIN_PASSWORD = 'b3whD7TzfIJ4'

