from app import create_app
from models.models import db, Categoria, Producto

app = create_app()

with app.app_context():
    # 🔹 Borra datos anteriores (opcional, para reiniciar)
    db.drop_all()
    db.create_all()

    # 🔹 Categorías
    herramientas = Categoria(nombre="Herramientas")
    hogar = Categoria(nombre="Hogar")
    jardin = Categoria(nombre="Jardín")

    db.session.add_all([herramientas, hogar, jardin])
    db.session.commit()

    # 🔹 Productos
    productos = [
        Producto(nombre="Martillo", descripcion="Martillo de acero reforzado", precio=50.0, imagen_url="/static/img/martillo.jpg", categoria_id=herramientas.id),
        Producto(nombre="Destornillador", descripcion="Destornillador de estrella", precio=25.0, imagen_url="/static/img/destornillador.jpg", categoria_id=herramientas.id),
        Producto(nombre="Silla", descripcion="Silla de madera para comedor", precio=300.0, imagen_url="/static/img/silla.jpg", categoria_id=hogar.id),
        Producto(nombre="Mesa", descripcion="Mesa rectangular de madera", precio=800.0, imagen_url="/static/img/mesa.jpg", categoria_id=hogar.id),
        Producto(nombre="Manguera", descripcion="Manguera de jardín 10m", precio=120.0, imagen_url="/static/img/manguera.jpg", categoria_id=jardin.id),
    ]

    db.session.add_all(productos)
    db.session.commit()

    print("✅ Base de datos inicializada con categorías y productos de prueba.")
