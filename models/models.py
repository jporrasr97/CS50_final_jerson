from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin  

db = SQLAlchemy()

# 🔹 Usuario
class Usuario(db.Model, UserMixin):  # 👈 hereda de UserMixin
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # idealmente debería ser hash
    rol = db.Column(db.String(10), default='cliente')  # cliente | admin


# 🔹 Categorías
class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

    productos = db.relationship('Producto', backref='categoria', lazy=True)

# 🔹 Productos
class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    precio = db.Column(db.Float, nullable=False)
    imagen_url = db.Column(db.String(200))
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'))

# 🔹 Pedidos
class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True)
    email_cliente = db.Column(db.String(120))  # para invitados
    fecha = db.Column(db.DateTime, server_default=db.func.now())
    estado = db.Column(db.String(20), default='pendiente')  # pendiente | entregado
    total = db.Column(db.Float, nullable=False)

    items = db.relationship('OrderItem', backref='pedido', lazy=True)

# 🔹 Items del pedido
class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedido.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)

    producto = db.relationship('Producto')
