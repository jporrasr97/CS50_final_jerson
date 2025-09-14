from flask import Blueprint, render_template, request, abort
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

@productos_bp.route('/producto/<int:id>')
def detalle_producto(id):
    producto = Producto.query.get_or_404(id)
    return render_template("producto_detalle.html", producto=producto)
