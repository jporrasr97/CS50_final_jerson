from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models.models import db, Usuario
from extensions import limiter

auth_bp = Blueprint('auth', __name__)

# Flask-Login setup (se hará en app.py)
login_manager = LoginManager()
login_manager.login_view = "auth.login"

# Adaptamos Usuario a UserMixin
class UsuarioLogin(Usuario, UserMixin):
    pass

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# 🔹 Registro
@auth_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        errores = []
        if not nombre or len(nombre) < 2:
            errores.append("El nombre debe tener al menos 2 caracteres.")
        if not email or '@' not in email:
            errores.append("Correo electrónico inválido.")
        if len(password) < 8:
            errores.append("La contraseña debe tener al menos 8 caracteres.")
        if Usuario.query.filter_by(email=email).first():
            errores.append("El correo ya está registrado.")

        if errores:
            for e in errores:
                flash(e, 'danger')
            return render_template('registro.html')

        password_hash = generate_password_hash(password)

        # Si es el primer usuario, hacerlo admin
        rol = 'admin' if Usuario.query.count() == 0 else 'cliente'

        nuevo_usuario = Usuario(nombre=nombre, email=email, password=password_hash, rol=rol)
        db.session.add(nuevo_usuario)
        db.session.commit()

        flash("Registro exitoso. Ahora inicia sesión.", 'success')
        return redirect(url_for('auth.login'))

    return render_template('registro.html')

# 🔹 Login
@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and check_password_hash(usuario.password, password):
            login_user(usuario)
            return redirect(url_for('home'))

        flash("Correo o contraseña incorrectos.")
        return redirect(url_for('auth.login'))

    return render_template('login.html')

# 🔹 Logout
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))
