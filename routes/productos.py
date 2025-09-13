from flask import Blueprint, render_template, request
from models.models import db, Producto, Categoria

productos_bp = Blueprint('productos', __name__)

@productos_bp.route('/productos')
def listar_productos():
    search = request.args.get('search', '')
    categoria_id = request.args.get('categoria', type=int)

    query = Producto.query
    if search:
        query = query.filter(Producto.nombre.ilike(f"%{search}%"))
    if categoria_id:
        query = query.filter_by(categoria_id=categoria_id)

    productos = query.all()
    categorias = Categoria.query.all()
    return render_template("productos.html", productos=productos, categorias=categorias, search=search, categoria_id=categoria_id)
