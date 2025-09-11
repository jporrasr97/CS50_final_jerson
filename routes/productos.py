from flask import Blueprint, render_template, request
from models.models import db, Producto

productos_bp = Blueprint('productos', __name__)

@productos_bp.route('/productos')
def listar_productos():
    search = request.args.get('search', '')
    if search:
        productos = Producto.query.filter(Producto.nombre.ilike(f"%{search}%")).all()
    else:
        productos = Producto.query.all()
    return render_template("productos.html", productos=productos)
