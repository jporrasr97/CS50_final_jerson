# routes/carrito.py
from flask import Blueprint, render_template, session, redirect, url_for, flash, request, current_app, jsonify
from flask_login import current_user, login_required
from models.models import db, Producto, Pedido, OrderItem
from flask_mail import Message
from extensions import mail  # ver paso 2

carrito_bp = Blueprint('carrito', __name__)

def _get_cart_item(carrito, producto_id):
    for item in carrito:
        if item['id'] == producto_id:
            return item
    return None

def _total_items():
    return sum(item['cantidad'] for item in session.get("carrito", []))

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

    # Stock disponible (si la columna no existe aún en BD, asume alto para no bloquear)
    stock_disp = getattr(producto, 'stock', None)
    max_qty = stock_disp if isinstance(stock_disp, int) and stock_disp >= 0 else 999999

    # buscar si ya está en el carrito
    item = _get_cart_item(session["carrito"], producto.id)
    if item:
        if item['cantidad'] >= max_qty:
            flash("No hay suficiente stock para agregar más unidades de este producto.")
        else:
            item['cantidad'] += 1
            session.modified = True
    else:
        if max_qty <= 0:
            flash("Producto agotado.")
        else:
            session["carrito"].append({
                'id': producto.id,
                'nombre': producto.nombre,
                'precio': producto.precio,
                'cantidad': 1
            })
            session.modified = True

    # Redirigir de vuelta a la página de productos en lugar del carrito
    return redirect(url_for('productos.listar_productos'))

@carrito_bp.route('/comprar-ahora/<int:id>')
def comprar_ahora(id):
    init_carrito()
    producto = Producto.query.get_or_404(id)

    # Respetar stock como en agregar_al_carrito
    stock_disp = getattr(producto, 'stock', None)
    max_qty = stock_disp if isinstance(stock_disp, int) and stock_disp >= 0 else 999999

    item = _get_cart_item(session["carrito"], producto.id)
    if item:
        if item['cantidad'] >= max_qty:
            flash("No hay suficiente stock para agregar más unidades de este producto.")
        else:
            item['cantidad'] += 1
            session.modified = True
    else:
        if max_qty <= 0:
            flash("Producto agotado.")
        else:
            session["carrito"].append({
                'id': producto.id,
                'nombre': producto.nombre,
                'precio': producto.precio,
                'cantidad': 1
            })
            session.modified = True

    return redirect(url_for('carrito.ver_carrito'))

@carrito_bp.route('/aumentar/<int:id>')
def aumentar_cantidad(id):
    init_carrito()
    producto = Producto.query.get_or_404(id)
    stock_disp = getattr(producto, 'stock', None)
    max_qty = stock_disp if isinstance(stock_disp, int) and stock_disp >= 0 else 999999

    for item in session["carrito"]:
        if item['id'] == id:
            if item['cantidad'] >= max_qty:
                flash("No hay suficiente stock para agregar más unidades de este producto.")
            else:
                item['cantidad'] += 1
                session.modified = True
            break
    return redirect(url_for('carrito.ver_carrito'))

@carrito_bp.route('/disminuir/<int:id>')
def disminuir_cantidad(id):
    init_carrito()
    for item in session["carrito"]:
        if item['id'] == id:
            if item['cantidad'] > 1:
                item['cantidad'] -= 1
            break
    session.modified = True
    return redirect(url_for('carrito.ver_carrito'))

@carrito_bp.route('/eliminar/<int:id>')
def eliminar_del_carrito(id):
    init_carrito()
    session["carrito"] = [item for item in session["carrito"] if item['id'] != id]
    session.modified = True
    return redirect(url_for('carrito.ver_carrito'))

# -----------------------------
# API JSON para controles tipo Amazon
# -----------------------------
@carrito_bp.route('/api/carrito/estado', methods=['GET'])
def api_carrito_estado():
    init_carrito()
    data = {
        'items': {str(i['id']): i['cantidad'] for i in session["carrito"]},
        'total_items': _total_items()
    }
    return jsonify(ok=True, **data), 200

@carrito_bp.route('/api/carrito/agregar', methods=['POST'])
def api_carrito_agregar():
    init_carrito()
    payload = request.get_json(silent=True) or {}
    try:
        producto_id = int(payload.get('id'))
    except Exception:
        return jsonify(ok=False, mensaje="ID inválido"), 400
    delta = int(payload.get('delta', 1))
    if delta == 0:
        return jsonify(ok=True, cantidad=_get_cart_item(session["carrito"], producto_id)['cantidad'] if _get_cart_item(session["carrito"], producto_id) else 0, total_items=_total_items()), 200

    producto = Producto.query.get_or_404(producto_id)
    stock_disp = getattr(producto, 'stock', None)
    max_qty = stock_disp if isinstance(stock_disp, int) and stock_disp >= 0 else 999999

    item = _get_cart_item(session["carrito"], producto_id)
    current = item['cantidad'] if item else 0
    new_qty = current + delta

    if new_qty <= 0:
        # eliminar del carrito
        session["carrito"] = [i for i in session["carrito"] if i['id'] != producto_id]
        session.modified = True
        return jsonify(ok=True, cantidad=0, total_items=_total_items(), stock=stock_disp), 200

    if new_qty > max_qty:
        # no exceder stock
        if item:
            item['cantidad'] = max_qty
        else:
            if max_qty > 0:
                session["carrito"].append({
                    'id': producto.id,
                    'nombre': producto.nombre,
                    'precio': producto.precio,
                    'cantidad': max_qty
                })
        session.modified = True
        return jsonify(ok=False, cantidad=max_qty, total_items=_total_items(), stock=stock_disp, mensaje="Stock insuficiente"), 200

    # aplicar cambio
    if item:
        item['cantidad'] = new_qty
    else:
        session["carrito"].append({
            'id': producto.id,
            'nombre': producto.nombre,
            'precio': producto.precio,
            'cantidad': new_qty
        })
    session.modified = True
    return jsonify(ok=True, cantidad=new_qty, total_items=_total_items(), stock=stock_disp), 200

# ACEPTA GET y POST para evitar "Method Not Allowed" y enviar el pedido por correo
@carrito_bp.route('/pedidos')
@login_required
def ver_pedidos():
    pedidos = Pedido.query.filter_by(usuario_id=current_user.id).order_by(Pedido.fecha.desc()).all()
    return render_template('pedidos.html', pedidos=pedidos)

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
    email_cliente = request.form.get('email', '').strip() if not current_user.is_authenticated else current_user.email

    errores = []
    if not carrito:
        errores.append("El carrito está vacío.")
    if not direccion:
        errores.append("La dirección de envío es obligatoria.")
    if not telefono:
        errores.append("El número de teléfono es obligatorio.")
    if not current_user.is_authenticated and not email_cliente:
        errores.append("El correo electrónico es obligatorio para visitantes.")
    # Validación básica de teléfono (al menos 8 dígitos)
    if telefono and sum(c.isdigit() for c in telefono) < 8:
        errores.append("El número de teléfono parece inválido.")

    total = sum(item['precio'] * item['cantidad'] for item in carrito)

    if errores:
        for e in errores:
            flash(e)
        return render_template('carrito.html', carrito=carrito, total=total,
                               direccion=direccion, telefono=telefono, email=email_cliente), 400

    # Validar stock antes de crear el pedido
    faltantes = []
    for item in carrito:
        producto = Producto.query.get(item['id'])
        if not producto:
            faltantes.append(f"Producto ID {item['id']} no encontrado.")
            continue
        stock_disp = getattr(producto, 'stock', None)
        if isinstance(stock_disp, int):
            if item['cantidad'] > stock_disp:
                faltantes.append(f"{producto.nombre}: stock disponible {stock_disp}, solicitado {item['cantidad']}.")

    if faltantes:
        for f in faltantes:
            flash(f)
        return render_template('carrito.html', carrito=carrito, total=total,
                               direccion=direccion, telefono=telefono, email=email_cliente), 400

    # Guardar pedido en BD
    nuevo_pedido = Pedido(
        usuario_id=current_user.id if current_user.is_authenticated else None,
        email_cliente=email_cliente if not current_user.is_authenticated else None,
        total=total
    )
    db.session.add(nuevo_pedido)
    db.session.flush()  # Para obtener el ID del pedido

    # Guardar items del pedido y descontar stock
    for item in carrito:
        producto = Producto.query.get(item['id'])
        order_item = OrderItem(
            pedido_id=nuevo_pedido.id,
            producto_id=item['id'],
            cantidad=item['cantidad'],
            precio_unitario=item['precio']
        )
        db.session.add(order_item)
        # descontar stock si la columna existe
        stock_disp = getattr(producto, 'stock', None)
        if isinstance(stock_disp, int):
            producto.stock = max(0, stock_disp - item['cantidad'])

    db.session.commit()

    # Construir el correo
    subject = "Nuevo pedido - Tienda en Línea"
    recipient = "jersonprs31@gmail.com"

    # Cuerpo de texto
    lineas = [f"- {i['nombre']} x{i['cantidad']} = Q{i['precio'] * i['cantidad']}" for i in carrito]
    texto_items = "\n".join(lineas)
    text_body = (
        f"Nuevo pedido:\n\n"
        f"Dirección de envío: {direccion}\n"
        f"Teléfono: {telefono}\n"
        f"Email cliente: {email_cliente}\n\n"
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
       <strong>Teléfono:</strong> {telefono}<br>
       <strong>Email cliente:</strong> {email_cliente}</p>
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
        return render_template('carrito.html', carrito=carrito, total=total,
                               direccion=direccion, telefono=telefono, email=email_cliente), 500