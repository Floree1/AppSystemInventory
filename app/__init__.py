from flask import Flask, request, session, g
from flask_babel import Babel
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from inventory_system.config import Config
from inventory_system.db.models import db, User, init_db
from werkzeug.security import generate_password_hash

bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'
babel = Babel()

def get_locale():
    if 'locale' in session:
        return session['locale']
    return request.accept_languages.best_match(Config.LANGUAGES)

@login_manager.user_loader
def load_user(user_id):
    # This now uses the correct tenant database because of the before_request handler
    return User.query.get(int(user_id))

def create_app(config_class=Config):
    app = Flask(__name__, template_folder='../ui/templates', static_folder='../ui/static')
    app.config.from_object(Config)

    @app.before_request
    def before_request_handler():
        # Set the database URI based on the session.
        # This makes the app connect to the correct tenant's database for each request.
        if 'db_uri' in session:
            # A new engine will be created by SQLAlchemy because the config changed.
            app.config['SQLALCHEMY_DATABASE_URI'] = session.get('db_uri')
        else:
            # Fallback to the default database if no tenant is in session
            # This is used for the login page and the tenant management page
            app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    babel.init_app(app, locale_selector=get_locale)

    from inventory_system.auth.auth import auth_bp
    app.register_blueprint(auth_bp)

    from inventory_system.app.routes import main_bp
    app.register_blueprint(main_bp)
    
    from inventory_system.app.products import products_bp
    app.register_blueprint(products_bp)

    from inventory_system.app.providers import providers_bp
    app.register_blueprint(providers_bp)

    from inventory_system.app.movements import movements_bp
    app.register_blueprint(movements_bp)

    from inventory_system.app.users import users_bp
    app.register_blueprint(users_bp)

    from inventory_system.app.reports import reports_bp
    app.register_blueprint(reports_bp)

    from inventory_system.app.tenant_admin import tenant_admin_bp
    from inventory_system.app.tenant_admin import tenant_admin_bp
    app.register_blueprint(tenant_admin_bp)

    from inventory_system.app.profile_routes import profile_bp
    app.register_blueprint(profile_bp)

    with app.app_context():
        # This will create tables for the fallback database.
        # Tenant databases will be created on demand.
        db.create_all()
        create_admin_user()

    return app

def create_admin_user():
    # This creates an admin user for the default/fallback database.
    # Each tenant will have their own admin user created on tenant creation.
    if not User.query.filter_by(username='admin').first():
        hashed_password = generate_password_hash('password')
        admin = User(username='admin', password_hash=hashed_password, role='admin')
        db.session.add(admin)
        db.session.commit()
        print("Default admin user created.")
