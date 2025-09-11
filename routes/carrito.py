# routes/carrito.py
from flask import Blueprint, render_template, session, redirect, url_for, flash, request, current_app
from models.models import Producto
from flask_mail import Message
from extensions import mail  # ver paso 2

carrito_bp = Blueprint('carrito', __name__)

# inicializar carrito en la sesión si no existe
def init_carrito():
    if "carrito" not in session:
        session["carrito"] = []

@carrito_bp.route('/carrito')
def ver_carrito():
    init_carrito()
    total = sum(item['precio'] * item['cantidad'] for item in session["carrito"])
    return render_template("carrito.html", carrito=session["carrito"], total=total)

@carrito_bp.route('/agregar/<int:id>')
def agregar_al_carrito(id):
    init_carrito()
    producto = Producto.query.get_or_404(id)

    # buscar si ya está en el carrito
    for item in session["carrito"]:
        if item['id'] == producto.id:
            item['cantidad'] += 1
            break
    else:
        session["carrito"].append({
            'id': producto.id,
            'nombre': producto.nombre,
            'precio': producto.precio,
            'cantidad': 1
        })

    session.modified = True
    return redirect(url_for('carrito.ver_carrito'))

@carrito_bp.route('/eliminar/<int:id>')
def eliminar_del_carrito(id):
    init_carrito()
    session["carrito"] = [item for item in session["carrito"] if item['id'] != id]
    session.modified = True
    return redirect(url_for('carrito.ver_carrito'))

# ACEPTA GET y POST para evitar "Method Not Allowed" y enviar el pedido por correo
@carrito_bp.route('/checkout', methods=['GET', 'POST'])
def checkout():
    init_carrito()
    carrito = session["carrito"]

    if request.method == 'GET':
        if not carrito:
            flash("Tu carrito está vacío.")
            return redirect(url_for('carrito.ver_carrito'))
        total = sum(item['precio'] * item['cantidad'] for item in carrito)
        return render_template('checkout.html', carrito=carrito, total=total)

    # POST: Confirmar pedido
    direccion = request.form.get('direccion', '').strip()
    telefono = request.form.get('telefono', '').strip()

    errores = []
    if not carrito:
        errores.append("El carrito está vacío.")
    if not direccion:
        errores.append("La dirección de envío es obligatoria.")
    if not telefono:
        errores.append("El número de teléfono es obligatorio.")
    # Validación básica de teléfono (al menos 8 dígitos)
    if telefono and sum(c.isdigit() for c in telefono) < 8:
        errores.append("El número de teléfono parece inválido.")

    total = sum(item['precio'] * item['cantidad'] for item in carrito)

    if errores:
        for e in errores:
            flash(e)
        return render_template('checkout.html', carrito=carrito, total=total,
                               direccion=direccion, telefono=telefono), 400

    # Construir el correo
    subject = "Nuevo pedido - Tienda en Línea"
    recipient = "jersonprs31@gmail.com"

    # Cuerpo de texto
    lineas = [f"- {i['nombre']} x{i['cantidad']} = Q{i['precio'] * i['cantidad']}" for i in carrito]
    texto_items = "\n".join(lineas)
    text_body = (
        f"Nuevo pedido:\n\n"
        f"Dirección de envío: {direccion}\n"
        f"Teléfono: {telefono}\n\n"
        f"Productos:\n{texto_items}\n\n"
        f"Total: Q{total}\n"
    )

    # Cuerpo HTML
    filas = "".join(
        f"<tr><td>{i['nombre']}</td><td>{i['cantidad']}</td><td>Q{i['precio']}</td><td>Q{i['precio'] * i['cantidad']}</td></tr>"
        for i in carrito
    )
    html_body = f"""
    <h3>Nuevo pedido</h3>
    <p><strong>Dirección de envío:</strong> {direccion}<br>
       <strong>Teléfono:</strong> {telefono}</p>
    <table border="1" cellpadding="6" cellspacing="0">
      <thead>
        <tr><th>Producto</th><th>Cantidad</th><th>Precio</th><th>Subtotal</th></tr>
      </thead>
      <tbody>
        {filas}
      </tbody>
    </table>
    <h4>Total: Q{total}</h4>
    """

    try:
        msg = Message(subject=subject, recipients=[recipient])
        msg.body = text_body
        msg.html = html_body
        mail.send(msg)

        # Vaciar carrito y confirmar
        session["carrito"] = []
        session.modified = True
        flash("¡Pedido confirmado! Te contactaremos pronto.")
        return redirect(url_for('productos.listar_productos'))

    except Exception as e:
        current_app.logger.exception("Error enviando correo de pedido")
        flash("No pudimos enviar el correo del pedido. Intenta más tarde.")
        return render_template('checkout.html', carrito=carrito, total=total,
                               direccion=direccion, telefono=telefono), 500