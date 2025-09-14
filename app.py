# app.py
import os
import secrets
from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_wtf import csrf_token
from models.models import db, Usuario, Producto, Categoria
from routes.auth import auth_bp
from routes.productos import productos_bp
from routes.carrito import carrito_bp
from routes.admin import admin_bp
from extensions import mail, limiter, talisman  # NUEVO: instancia de Flask-Mail, Limiter y Talisman

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

login_manager = LoginManager()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # Config básica
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(32))
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URI',
        'sqlite:///' + os.path.join(app.instance_path, 'tienda.db')
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Asegúrate de que existe la carpeta instance/
    os.makedirs(app.instance_path, exist_ok=True)

    # Config de correo (Gmail SMTP por defecto)
    app.config.update(
        MAIL_SERVER=os.getenv('MAIL_SERVER', 'smtp.gmail.com'),
        MAIL_PORT=int(os.getenv('MAIL_PORT', 587)),
        MAIL_USE_TLS=os.getenv('MAIL_USE_TLS', 'true').lower() in ('true', '1', 'yes', 'y', 'on'),
        MAIL_USERNAME=os.getenv('MAIL_USERNAME'),           # sin default sensible
        MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
        MAIL_DEFAULT_SENDER=os.getenv('MAIL_DEFAULT_SENDER') or os.getenv('MAIL_USERNAME'),
        # Opcional: no intentar enviar si faltan credenciales (útil en dev)
        MAIL_SUPPRESS_SEND=not (os.getenv('MAIL_USERNAME') and os.getenv('MAIL_PASSWORD')),
    )

    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    talisman.init_app(app, content_security_policy=None)  # Adjust CSP as needed
    app.jinja_env.globals['csrf_token'] = csrf_token

    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return db.session.get(Usuario, int(user_id))
        except Exception:
            return None

    # Registrar blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(productos_bp)
    app.register_blueprint(carrito_bp)
    app.register_blueprint(admin_bp)

    # Ruta principal
    @app.route('/')
    def home():
        if Usuario.query.count() == 0:
            return redirect(url_for('auth.registro'))

        # Obtener productos destacados (últimos 12 productos)
        productos = Producto.query.order_by(Producto.id.desc()).limit(12).all()
        categorias = Categoria.query.all()

        return render_template('index.html', productos=productos, categorias=categorias)

    # Crear tablas si no existen
    with app.app_context():
        db.create_all()

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('500.html'), 500

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)