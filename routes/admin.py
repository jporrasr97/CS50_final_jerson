from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.models import db, Producto, Categoria

# Prefijo /admin para todas las rutas de este blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or getattr(current_user, 'rol', None) != 'admin':
            flash("No tienes permisos para acceder al panel de administración.", "warning")
            return redirect(url_for('productos.listar_productos'))
        return f(*args, **kwargs)
    return wrapper

# Dashboard del admin -> endpoint: admin.dashboard
@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    productos = Producto.query.all()
    categorias = Categoria.query.all()
    return render_template("admin.html", productos=productos, categorias=categorias)

# ------------------------
# PRODUCTOS
# ------------------------

# Agregar producto
@admin_bp.route('/producto/agregar', methods=['GET', 'POST'])
@login_required
@admin_required
def agregar_producto():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        precio = request.form.get('precio', type=float)
        imagen_url = request.form.get('imagen_url')
        categoria_id = request.form.get('categoria_id', type=int)

        if not nombre or precio is None:
            flash("Nombre y precio son obligatorios.", "warning")
            return redirect(url_for('admin.agregar_producto'))

        nuevo = Producto(
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            imagen_url=imagen_url,
            categoria_id=categoria_id
        )
        db.session.add(nuevo)
        db.session.commit()
        flash("Producto agregado con éxito.", "success")
        return redirect(url_for('admin.dashboard'))

    categorias = Categoria.query.all()
    return render_template("admin_form_producto.html", categorias=categorias)

# Editar producto
@admin_bp.route('/producto/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_producto(id):
    producto = Producto.query.get_or_404(id)

    if request.method == 'POST':
        producto.nombre = request.form.get('nombre')
        producto.descripcion = request.form.get('descripcion')
        producto.precio = request.form.get('precio', type=float)
        producto.imagen_url = request.form.get('imagen_url')
        producto.categoria_id = request.form.get('categoria_id', type=int)

        db.session.commit()
        flash("Producto actualizado con éxito.", "success")
        return redirect(url_for('admin.dashboard'))

    categorias = Categoria.query.all()
    return render_template("admin_form_producto.html", producto=producto, categorias=categorias)

# Eliminar producto
@admin_bp.route('/producto/eliminar/<int:id>', methods=['POST', 'GET'])
@login_required
@admin_required
def eliminar_producto(id):
    producto = Producto.query.get_or_404(id)
    db.session.delete(producto)
    db.session.commit()
    flash("Producto eliminado.", "info")
    return redirect(url_for('admin.dashboard'))

# ------------------------
# CATEGORÍAS
# ------------------------

# Agregar categoría
@admin_bp.route('/categoria/agregar', methods=['GET', 'POST'])
@login_required
@admin_required
def agregar_categoria():
    if request.method == 'POST':
        nombre = (request.form.get('nombre') or '').strip()
        if not nombre:
            flash("El nombre de la categoría es obligatorio.", "warning")
            return redirect(url_for('admin.dashboard'))

        nueva = Categoria(nombre=nombre)
        db.session.add(nueva)
        db.session.commit()
        flash("Categoría agregada.", "success")
        return redirect(url_for('admin.dashboard'))

    # Si es GET, muestra el formulario
    return render_template("admin_form_categoria.html")

# Eliminar categoría
@admin_bp.route('/categoria/eliminar/<int:id>', methods=['POST', 'GET'])
@login_required
@admin_required
def eliminar_categoria(id):
    categoria = Categoria.query.get_or_404(id)
    db.session.delete(categoria)
    db.session.commit()
    flash("Categoría eliminada.", "info")
    return redirect(url_for('admin.dashboard'))

# Editar categoría
@admin_bp.route('/categoria/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_categoria(id):
    categoria = Categoria.query.get_or_404(id)

    if request.method == 'POST':
        nombre = (request.form.get('nombre') or '').strip()
        if not nombre:
            flash("El nombre de la categoría es obligatorio.", "warning")
            return redirect(url_for('admin.editar_categoria', id=id))

        categoria.nombre = nombre
        db.session.commit()
        flash("Categoría actualizada con éxito.", "success")
        return redirect(url_for('admin.dashboard'))

    return render_template("admin_form_categoria.html", categoria=categoria)
