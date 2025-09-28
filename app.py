# app.py
import os
import secrets
from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager
from models.models import db, Usuario, Producto, Categoria
from routes.auth import auth_bp
from routes.productos import productos_bp
from routes.carrito import carrito_bp
from routes.admin import admin_bp
from extensions import mail, limiter, talisman  # NUEVO: instancia de Flask-Mail, Limiter y Talisman
from sqlalchemy import text

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

login_manager = LoginManager()

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

    # Carpeta de uploads para imágenes (drag & drop admin)
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

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
        # Configurar backend de almacenamiento para Flask-Limiter (evita warning en dev)
        RATELIMIT_STORAGE_URI=os.getenv('RATELIMIT_STORAGE_URI', 'memory://'),
    )

    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)
    talisman.init_app(app, content_security_policy=None)  # Adjust CSP as needed

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

    # Favicon: evita 404 del navegador solicitando /favicon.ico
    @app.route('/favicon.ico')
    def favicon():
        return redirect(url_for('static', filename='img/zapato.PNG'))

    # Crear tablas si no existen y asegurar columna 'stock' en 'producto' (SQLite)
    with app.app_context():
        db.create_all()
        try:
            res = db.session.execute(text("PRAGMA table_info('producto')")).fetchall()
            cols = {row[1] for row in res}  # (cid, name, type, ... )
            if 'stock' not in cols:
                db.session.execute(text("ALTER TABLE producto ADD COLUMN stock INTEGER NOT NULL DEFAULT 0"))
                db.session.commit()
        except Exception:
            app.logger.exception("No se pudo verificar/agregar columna 'stock' en la tabla producto")

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