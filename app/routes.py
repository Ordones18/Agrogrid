# =================== Importaciones principales ===================
from app.grafo_transporte import grafo_cantonal, dijkstra # Importaciones para el grafo de transporte
from flask import render_template, request, redirect, url_for, flash, session, send_file, jsonify  # Funciones principales de Flask para manejo de vistas, formularios, sesiones y respuestas
from app import app, mail, db  # Instancias principales de la app, correo y base de datos
from flask_login import current_user, login_required, login_user
from flask_mail import Message  # Para enviar correos electrónicos
from app.models import Usuario, Producto, Categoria, Subcategoria, Carrito  # Modelos de la base de datos
from werkzeug.security import generate_password_hash, check_password_hash  # Utilidades para hashear y verificar contraseñas
from app.utils import generate_token, confirm_token  # Funciones utilitarias para manejo de tokens (recuperación de contraseña, etc.)
from werkzeug.utils import secure_filename  # Para guardar archivos de forma segura
import os  # Manejo de rutas y sistema operativo
from flask import current_app  # Acceso a la app actual de Flask
import networkx as nx  # Usado solo en grafo_productos
from app.ubicacion import obtener_estructura_ubicacion  # Usado en APIs de ubicación
# --- API para menús jerárquicos ---
from app.taxonomia import obtener_taxonomia_catalogo  # Usado en APIs de taxonomía

@app.route('/api/categorias')
def api_categorias():
    categorias = Categoria.query.order_by(Categoria.nombre).all()
    return jsonify([{'id': c.id, 'nombre': c.nombre} for c in categorias])



@app.route('/api/productos/<int:subcategoria_id>')
def api_productos(subcategoria_id):
    productos = Producto.query.filter_by(subcategoria_id=subcategoria_id).order_by(Producto.nombre).all()
    return jsonify([{'id': p.id, 'nombre': p.nombre} for p in productos])



# =================== Rutas Públicas (sin login) ===================

@app.route('/api/ubicacion/estructura')
def api_ubicacion_estructura():
    """
    Devuelve la estructura de ubicaciones: {region: {provincia: [cantones]}}
    """
    estructura = obtener_estructura_ubicacion()
    return jsonify(estructura)


@app.route('/api/calcular_transporte', methods=['GET', 'POST'])
def api_calcular_transporte():
    """
    Calcula la ruta más corta y el tipo de transporte entre dos cantones usando Dijkstra.
    Recibe origen y destino por GET o POST.
    Devuelve JSON con distancia, ruta, tipos de tramo y si incluye barco.
    """
    data = request.get_json() if request.method == 'POST' else request.args
    import unicodedata
    def normaliza(nombre):
        return unicodedata.normalize('NFKD', nombre).encode('ASCII', 'ignore').decode('ASCII').strip().upper()
    origen = data.get('origen')
    destino = data.get('destino')
    if not origen or not destino:
        return jsonify({'error': 'Debes indicar origen y destino'}), 400

    # Buscar el nombre real en el grafo (mayúsculas y sin tildes)
    origen_norm = normaliza(origen)
    destino_norm = normaliza(destino)
    claves_grafo = {normaliza(k): k for k in grafo_cantonal.keys()}
    origen_real = claves_grafo.get(origen_norm)
    destino_real = claves_grafo.get(destino_norm)
    if not origen_real or not destino_real:
        return jsonify({'error': 'Cantón no encontrado'}), 404

    distancia, ruta, tipos = dijkstra(grafo_cantonal, origen_real, destino_real)
    if distancia == float('inf'):
        return jsonify({'error': 'Ruta no encontrada'}), 404
    incluye_maritimo = 'maritimo' in tipos

    # Calcular tiempo total estimado (en minutos y formato hh:mm)
    tiempo_total_min = 0
    if ruta and len(ruta) > 1:
        for i in range(len(ruta)-1):
            tramo = grafo_cantonal[ruta[i]][ruta[i+1]]
            tiempo_total_min += tramo.get('tiempo', 0)
    horas = int(tiempo_total_min // 60)
    minutos = int(tiempo_total_min % 60)
    tiempo_legible = f"{horas:02}:{minutos:02}"

    # Calcular costo de envío
    def calcular_costo_envio(distancia_km, tipos):
        tarifa_base = 3.00
        km_incluidos = 10
        costo_por_km = 0.30
        recargo_maritimo = 10.00 if 'maritimo' in tipos else 0.00
        if distancia_km <= km_incluidos:
            return tarifa_base + recargo_maritimo
        else:
            return tarifa_base + (distancia_km - km_incluidos) * costo_por_km + recargo_maritimo
    costo_envio = round(calcular_costo_envio(distancia, tipos), 2)

    return jsonify({
        'distancia': distancia,
        'ruta': ruta,
        'tipos': list(sorted(set(tipos))),
        'incluye_maritimo': incluye_maritimo,
        'tiempo_min': round(tiempo_total_min, 2),
        'tiempo_legible': tiempo_legible,
        'costo_envio': costo_envio
    })

# Incluye home, about, explore, catálogo, etc.

@app.route('/api/taxonomia/catalogo')
def api_taxonomia_catalogo():
    """
    Devuelve la estructura de categorías, subcategorías y productos de catálogo para el selector de productos.
    """
    return jsonify(obtener_taxonomia_catalogo())

@app.route('/')
def index():
    """
    Página de inicio de AgroGrid.
    - Método: GET
    - Request: Ninguno
    - Response: Renderiza index.html
    """
    user = session.get('user')
    user_type = session.get('user_type')
    return render_template('index.html', user=user, user_type=user_type)

@app.route('/about')
def about():
    """
    Página de información sobre AgroGrid.
    - Método: GET
    - Request: Ninguno
    - Response: Renderiza about.html
    """
    return render_template('about.html')

@app.route('/explore')
def explore():
    """
    Página para explorar productos/agricultores.
    - Método: GET
    - Request: Ninguno
    - Response: Renderiza explore.html
    """
    return render_template('explore.html')

# =================== Autenticación y Registro ===================
# Incluye registro, login, logout, recuperación y reset de contraseña.

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Registro de nuevos usuarios.
    - Métodos: GET, POST
    - Request (POST): name, email, user_type, provincia, cedula, phone, password
    - Response: Redirige a login o renderiza register.html
    """
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        user_type = request.form['user_type']
        provincia = request.form['provincia']
        cedula = request.form['cedula']
        phone = request.form['phone']
        password = generate_password_hash(request.form['password'])
        # Verifica si el usuario ya existe
        if Usuario.query.filter_by(email=email).first():
            flash('El correo ya está registrado inicia sesión.', 'danger')
            return redirect(url_for('login'))
        usuario = Usuario(
            name=name,
            email=email,
            user_type=user_type,
            provincia=provincia,
            cedula=cedula,
            phone=phone,
            password=password
        )
        db.session.add(usuario)
        db.session.commit()
        # Envía el correo de bienvenida
        msg = Message('¡Bienvenido a AgroGrid System!',
                      sender=app.config['MAIL_USERNAME'],
                      recipients=[email])
        msg.body = f'Hola {name},\n\n¡Gracias por registrarte en AgroGrid System!'
        msg.html = render_template('email/welcome.html', name=name, user_type=user_type)
        mail.send(msg)
        mail.send(msg)

        # Guarda el mensaje en la sesión para que persista tras la redirección
        flash('¡Cuenta creada correctamente! Verifica tu correo.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Inicio de sesión de usuario.
    - Métodos: GET, POST
    - Request (POST): email, password
    - Response: Redirige a perfil según tipo o renderiza login.html
    """
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and check_password_hash(usuario.password, password):
            login_user(usuario)  # Autentica el usuario con Flask-Login
            session['user'] = usuario.email
            session['user_type'] = usuario.user_type  # Guardamos el tipo de usuario en la sesión

            # Redireccionamos según el tipo de usuario
            if usuario.user_type == 'agricultor':
                return redirect(url_for('perfil_agricultor'))
            elif usuario.user_type == 'comprador':
                return redirect(url_for('perfil_comprador'))
            elif usuario.user_type == 'transportista':
                return redirect(url_for('perfil_transportista'))
            else:
                return redirect(url_for('perfil'))  # Perfil genérico por defecto
        else:
            flash('Correo o contraseña incorrectos', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    """
    Cierra la sesión del usuario.
    - Método: GET
    - Request: Ninguno
    - Response: Redirige a login
    """
    session.clear()
    flash('Has cerrado sesión exitosamente.', 'success')
    return redirect(url_for('login'))

@app.route('/recover_password', methods=['GET', 'POST'])
def recover_password():
    """
    Recuperación de contraseña por cédula.
    - Métodos: GET, POST
    - Request (POST): cedula
    - Response: Envía email de recuperación o renderiza recover_password.html
    """
    if request.method == 'POST':
        cedula = request.form['cedula']
        user = Usuario.query.filter_by(cedula=cedula).first()
        if user:
            token = generate_token(user.email)
            recover_url = url_for('reset_password', token=token, _external=True)
            msg = Message('Recupera tu contraseña', sender=app.config['MAIL_USERNAME'], recipients=[user.email])
            msg.body = f'Para restablecer tu contraseña haz clic aquí: {recover_url}'
            try:
                mail.send(msg)
                flash('Se ha enviado un correo con instrucciones para restablecer tu contraseña.', 'success')
            except Exception as e:
                flash(f'Error al enviar el correo: {e}', 'danger')
        else:
            flash('No se encontró un usuario con esa cédula.', 'danger')
    return render_template('recover_password.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """
    Restablecimiento de contraseña mediante token enviado por email.
    - Métodos: GET, POST
    - Request (POST): password
    - Response: Redirige a login o renderiza reset_password.html
    """
    email = confirm_token(token)
    if not email:
        flash('El enlace es inválido o ha expirado.', 'danger')
        return redirect(url_for('recover_password'))
    if request.method == 'POST':
        password = request.form['password']
        user = Usuario.query.filter_by(email=email).first()
        if user:
            user.set_password(password)  # Implementa este método en tu modelo
            db.session.commit()
            flash('Contraseña actualizada correctamente.', 'success')
            return redirect(url_for('login'))
    return render_template('reset_password.html')

# =================== Perfiles de Usuario ===================
# Paneles de agricultor, comprador, transportista, y APIs relacionadas.

from flask_login import login_required, current_user
from flask import jsonify

@app.route('/favoritos/agregar/<int:producto_id>', methods=['POST'])
@login_required
def agregar_favorito(producto_id):
    if getattr(current_user, 'user_type', None) != 'comprador':
        return jsonify({'success': False, 'error': 'Solo compradores pueden agregar favoritos.'}), 403
    from app.models import Producto
    producto = Producto.query.get(producto_id)
    if not producto:
        return jsonify({'success': False, 'error': 'Producto no encontrado.'}), 404
    if producto not in current_user.favoritos:
        current_user.favoritos.append(producto)
        from app import db
        db.session.commit()
    return jsonify({'success': True})

@app.route('/favoritos/quitar/<int:producto_id>', methods=['POST'])
@login_required
def quitar_favorito(producto_id):
    if getattr(current_user, 'user_type', None) != 'comprador':
        return jsonify({'success': False, 'error': 'Solo compradores pueden quitar favoritos.'}), 403
    from app.models import Producto
    producto = Producto.query.get(producto_id)
    if not producto:
        return jsonify({'success': False, 'error': 'Producto no encontrado.'}), 404
    if producto in current_user.favoritos:
        current_user.favoritos.remove(producto)
        from app import db
        db.session.commit()
    return jsonify({'success': True})

@app.route('/api/registrar_vista_rapida', methods=['POST'])
def api_registrar_vista_rapida():
    """
    Recibe un producto_id por POST y suma 1 al campo vistas del producto.
    Devuelve JSON con el nuevo total de vistas.
    """
    from flask import request, jsonify
    producto_id = request.json.get('producto_id')
    if not producto_id:
        return jsonify({'error': 'Falta producto_id'}), 400
    producto = Producto.query.get(producto_id)
    if not producto:
        return jsonify({'error': 'Producto no encontrado'}), 404
    producto.vistas = (producto.vistas or 0) + 1
    db.session.commit()
    return jsonify({'vistas': producto.vistas})


@app.route('/perfil/agricultor')
def perfil_agricultor():
    """
    Panel de control del agricultor autenticado.
    - Método: GET
    - Requiere autenticación como agricultor.
    - Response: Renderiza agricultor/perfil_agricultor.html
    """
    if 'user' not in session or session.get('user_type') != 'agricultor':
        flash('Acceso no autorizado.', 'danger')
        return redirect(url_for('login'))

    usuario = Usuario.query.filter_by(email=session['user']).first()
    if not usuario:
        flash('Usuario no encontrado.', 'danger')
        session.pop('user', None)
        session.pop('user_type', None)
        return redirect(url_for('login'))

    productos_del_agricultor = Producto.query.filter_by(usuario_id=usuario.id).all()
    # --- Lógica para calcular ventas totales reales ---
    from app.analytics import calcular_ventas_agregadas
    # Obtener todos los productos del agricultor
    productos = productos_del_agricultor
    producto_ids = [p.id for p in productos]
    producto_map = {p.id: p.nombre for p in productos}
    # Obtener todos los items de orden relacionados a estos productos
    orden_items = (
        db.session.query(OrdenItem, Orden)
        .join(Orden, OrdenItem.orden_id == Orden.id)
        .filter(OrdenItem.producto_id.in_(producto_ids))
        .all()
    )
    ventas_totales_data = calcular_ventas_agregadas(orden_items, producto_map)
    ventas_totales_calculadas = ventas_totales_data.get('total_general', 0.0)
    numero_productos_publicados = len(productos_del_agricultor)
    vistas_a_productos = 0

    # Obtener todas las ventas (órdenes) que incluyan productos de este agricultor
    ventas = (
        db.session.query(Orden, OrdenItem, Producto, Usuario)
        .join(OrdenItem, Orden.id == OrdenItem.orden_id)
        .join(Producto, OrdenItem.producto_id == Producto.id)
        .join(Usuario, Orden.comprador_id == Usuario.id)
        .filter(Producto.usuario_id == usuario.id)
        .order_by(Orden.creado_en.desc())
        .all()
    )

    return render_template('agricultor/perfil_agricultor.html',
                           user=usuario,
                           productos=productos_del_agricultor,
                           ventas=ventas,
                           ventas_totales=ventas_totales_calculadas,
                           numero_productos=numero_productos_publicados,
                           vistas_productos=vistas_a_productos,
                           user_type=session['user_type'])

@app.route('/perfil/comprador')
def perfil_comprador():
    """
    Panel de control del comprador autenticado.
    - Método: GET
    - Requiere autenticación como comprador.
    - Response: Renderiza comprador/perfil_comprador.html
    """
    if 'user' not in session:
        return redirect(url_for('login'))
    if session.get('user_type') != 'comprador':
        flash('No tienes permiso para acceder a esta página', 'danger')
        return redirect(url_for('login'))

    usuario = Usuario.query.filter_by(email=session['user']).first()

    # --- LIMPIEZA DE DATOS HUÉRFANOS Y COSTO_ENVIO VACÍO ---
    from app.models import Orden, OrdenItem, Producto
    # Limpiar OrdenItems sin snapshot ni producto
    orden_items = OrdenItem.query.all()
    for item in orden_items:
        producto = Producto.query.get(item.producto_id)
        if not producto and not item.producto_nombre:
            db.session.delete(item)
    # Limpiar Órdenes sin items asociados
    ordenes = Orden.query.all()
    for orden in ordenes:
        items = OrdenItem.query.filter_by(orden_id=orden.id).all()
        if not items:
            db.session.delete(orden)
        # Actualizar costo_envio vacío
        if orden.costo_envio is None:
            orden.costo_envio = 0.0
    db.session.commit()
    # --- FIN LIMPIEZA ---

    # Asegúrate de que el usuario exista y maneja el caso contrario
    if not usuario:
        flash('Usuario no encontrado.', 'danger')
        session.pop('user', None)
        session.pop('user_type', None)
        return redirect(url_for('login'))

    # Obtener historial de pedidos
    from app.models import Orden, OrdenItem, Producto
    pedidos = Orden.query.filter_by(comprador_id=usuario.id).order_by(Orden.creado_en.desc()).all()
    pedidos_lista = []
    for pedido in pedidos:
        items = OrdenItem.query.filter_by(orden_id=pedido.id).all()
        productos = []
        for item in items:
            producto = Producto.query.get(item.producto_id)
            if producto:
                productos.append({
                    'nombre': producto.nombre,
                    'unidad': producto.unidad,
                    'cantidad': item.cantidad,
                    'precio': item.precio_unitario
                })
            else:
                # Producto eliminado, usar snapshot
                nombre = item.producto_nombre or 'Producto eliminado'
                unidad = item.producto_unidad or ''
                productos.append({
                    'nombre': nombre,
                    'unidad': unidad,
                    'cantidad': item.cantidad,
                    'precio': item.precio_unitario
                })
        # Estado real del viaje si existe
        estado_viaje = pedido.viaje.estado if hasattr(pedido, 'viaje') and pedido.viaje else pedido.estado
        viaje_id = pedido.viaje.id if hasattr(pedido, 'viaje') and pedido.viaje else None
        pedidos_lista.append({
            'fecha': pedido.creado_en,
            'productos': productos,
            'total': pedido.total,
            'costo_envio': pedido.costo_envio,
            'estado': estado_viaje,
            'viaje_id': viaje_id
        })

    # Obtener productos favoritos correctamente
    favoritos = usuario.favoritos.all()
    favoritos_count = len(favoritos)
    
    pedidos_realizados = len(pedidos_lista)
    return render_template('comprador/perfil_comprador.html',
                           user=usuario,
                           user_type=session['user_type'],
                           pedidos=pedidos_lista,
                           favoritos=favoritos,
                           favoritos_count=favoritos_count,
                           pedidos_realizados=pedidos_realizados)

# --- API para info de viaje para modal del comprador ---

@app.route('/api/calificar_transportista/<int:viaje_id>', methods=['POST'])
@login_required
def api_calificar_transportista(viaje_id):
    from app.models import Viaje, Orden
    viaje = Viaje.query.get(viaje_id)
    if not viaje:
        return jsonify({'msg': 'Viaje no encontrado'}), 404
    # Solo el comprador de la orden puede calificar y solo si ya está entregado
    if not viaje.orden or viaje.orden.comprador_id != current_user.id:
        return jsonify({'msg': 'No autorizado'}), 403
    if viaje.estado != 'entregado':
        return jsonify({'msg': 'Solo puedes calificar un viaje entregado'}), 400
    data = request.get_json()
    calificacion = data.get('calificacion')
    if not calificacion or not (1 <= int(calificacion) <= 5):
        return jsonify({'msg': 'Calificación inválida'}), 400
    viaje.calificacion = int(calificacion)
    db.session.commit()
    return jsonify({'msg': '¡Gracias por tu calificación!'})

@app.route('/api/info_viaje/<int:viaje_id>')
@login_required
def api_info_viaje(viaje_id):
    from app.models import Viaje, Usuario
    viaje = Viaje.query.get(viaje_id)
    if not viaje:
        return {'error': 'Viaje no encontrado'}, 404
    transportista = viaje.transportista
    if transportista:
        transportista_data = {
            'nombre': transportista.name,
            'email': transportista.email,
            'phone': transportista.phone,
        }
    else:
        transportista_data = None
    return {
        'transportista': transportista_data,
        'fecha_entrega': viaje.fecha_entrega.strftime('%d/%m/%Y') if viaje.fecha_entrega else None
    }

@app.route('/perfil/transportista')
def perfil_transportista():
    """
    Panel de control del transportista autenticado.
    - Método: GET
    - Requiere autenticación como transportista.
    - Response: Renderiza transportista/perfil_transportista.html
    """
    if 'user' not in session:
        return redirect(url_for('login'))
    if session.get('user_type') != 'transportista':
        flash('No tienes permiso para acceder a esta página', 'danger')
        return redirect(url_for('login'))

    usuario = Usuario.query.filter_by(email=session['user']).first()
    return render_template('transportista/perfil_transportista.html',
                           user=usuario,
                           user_type=session['user_type'])

# =================== APIs de Viajes para Transportista ===================
from app.models import Viaje, Orden
from datetime import datetime

@app.route('/api/viajes_pendientes')
@login_required
def api_viajes_pendientes():
    if current_user.user_type != 'transportista':
        return jsonify([])
    viajes = Viaje.query.filter_by(estado='pendiente').all()
    resultado = []
    for v in viajes:
        orden = v.orden
        agricultor = None
        productos = []
        if orden and orden.items:
            for item in orden.items:
                prod = item.producto
                if prod and not agricultor:
                    agricultor = prod.usuario.name
                if prod:
                    productos.append(f"{item.cantidad} {prod.unidad or ''} {prod.nombre}")
        comprador = orden.comprador_id if orden else None
        comprador_nombre = Usuario.query.get(comprador).name if comprador else ''
        resultado.append({
            'id': v.id,
            'origen': v.origen or '',
            'destino': v.destino or '',
            'productos': ', '.join(productos),
            'agricultor': agricultor or '',
            'comprador': comprador_nombre,
        })
    return jsonify(resultado)

@app.route('/api/viajes_asignados')
@login_required
def api_viajes_asignados():
    if current_user.user_type != 'transportista':
        return jsonify([])
    viajes = Viaje.query.filter(Viaje.transportista_id==current_user.id, Viaje.estado.in_(['aceptado','en_progreso','entregado'])).all()
    resultado = []
    for v in viajes:
        orden = v.orden
        productos = []
        if orden and orden.items:
            for item in orden.items:
                prod = item.producto
                if prod:
                    productos.append(f"{item.cantidad} {prod.unidad or ''} {prod.nombre}")
        resultado.append({
            'id': v.id,
            'origen': v.origen or '',
            'destino': v.destino or '',
            'productos': ', '.join(productos),
            'estado': v.estado
        })
    return jsonify(resultado)

@app.route('/api/aceptar_viaje/<int:viaje_id>', methods=['POST'])
@login_required
def api_aceptar_viaje(viaje_id):
    if current_user.user_type != 'transportista':
        return jsonify({'success': False, 'message': 'No autorizado'}), 403
    viaje = Viaje.query.get(viaje_id)
    if not viaje or viaje.estado != 'pendiente':
        return jsonify({'success': False, 'message': 'Viaje no disponible'}), 400
    viaje.transportista_id = current_user.id
    viaje.estado = 'en_progreso'
    viaje.fecha_asignacion = datetime.utcnow()
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/marcar_entregado/<int:viaje_id>', methods=['POST'])
@login_required
def api_marcar_entregado(viaje_id):
    if current_user.user_type != 'transportista':
        return jsonify({'success': False, 'message': 'No autorizado'}), 403
    viaje = Viaje.query.get(viaje_id)
    if not viaje or viaje.transportista_id != current_user.id or viaje.estado != 'en_progreso':
        return jsonify({'success': False, 'message': 'No permitido'}), 400
    viaje.estado = 'entregado'
    viaje.fecha_entrega = datetime.utcnow()
    db.session.commit()
    return jsonify({'success': True})

# =================== Gestión de Productos ===================
# Agregar, editar, eliminar productos.

@app.route('/producto/agregar', methods=['POST'])
def agregar_producto():
    """
    Agrega un nuevo producto agrícola para el agricultor autenticado.
    - Método: POST
    - Request: Datos del producto desde formulario
    - Response: Redirige a perfil_agricultor
    """
    if 'user' not in session or session.get('user_type') != 'agricultor':
        flash('Acceso no autorizado.', 'danger')
        return redirect(url_for('login'))

    usuario = Usuario.query.filter_by(email=session['user']).first()
    if not usuario:
        flash('Usuario no encontrado.', 'danger')
        return redirect(url_for('login'))

    # Recoge los datos del formulario
    nombre = request.form['productName']
    tipo = request.form['productType']
    region = request.form['region']
    provincia = request.form['provincia']
    inicial_nombre = nombre[0].upper() if nombre else ''
    imagen = request.files.get('productImage')
    # Manejo robusto del precio
    try:
        precio = float(request.form.get('productPrice', 0) or 0)
    except ValueError:
        precio = 0.0
    unidad = request.form.get('productUnit')
    descripcion = request.form.get('productDescription')
    cantidad = request.form.get('productQuantity')
    cantidad = float(cantidad) if cantidad else 0.0

    # Manejo de la imagen
    imagen_url = None
    if imagen and imagen.filename != '':
        filename = secure_filename(imagen.filename)
        uploads_dir = os.path.join(current_app.root_path, 'static', 'uploads')
        os.makedirs(uploads_dir, exist_ok=True)
        imagen.save(os.path.join(uploads_dir, filename))
        imagen_url = filename

    # Recoge el subcategoria_id del formulario
    print('DEBUG FORM KEYS:', list(request.form.keys()))
    subcat3_id = request.form.get('subcategoria3Selector')
    subcat2_id = request.form.get('subcategoria2Selector')
    subcategoria_id = subcat3_id if subcat3_id else subcat2_id
    if not subcategoria_id:
        flash('Debes seleccionar una subcategoría (nivel 2 o 3).', 'danger')
        return redirect(url_for('perfil_agricultor'))

    # Recoge el cantón del formulario
    canton = request.form.get('canton')

    # Crea el producto y lo guarda en la base de datos
    producto = Producto(
        nombre=nombre,
        tipo=tipo,
        region=region,
        provincia=provincia,
        canton=canton,
        inicial_nombre=inicial_nombre,
        imagen_url=imagen_url,
        usuario_id=usuario.id,
        precio=precio,
        unidad=unidad,
        descripcion=descripcion,
        cantidad=cantidad,
        subcategoria_id=subcategoria_id
    )
    db.session.add(producto)
    db.session.commit()

    flash('Producto agregado correctamente.', 'success')
    return redirect(url_for('perfil_agricultor'))

@app.route('/producto/editar/<int:producto_id>', methods=['GET', 'POST'])
def editar_producto(producto_id):
    """
    Edita un producto existente del agricultor autenticado.
    - Métodos: GET, POST
    - Request (POST): Nuevos datos del producto
    - Response: Redirige a perfil_agricultor o renderiza editar_producto.html
    """
    producto = Producto.query.get_or_404(producto_id)
    # Opcional: verifica que el usuario sea el dueño del producto
    if 'user' not in session or session.get('user_type') != 'agricultor' or producto.usuario.email != session['user']:
        flash('Acceso no autorizado.', 'danger')
        return redirect(url_for('perfil_agricultor'))

    if request.method == 'POST':
        producto.nombre = request.form['productName']
        producto.tipo = request.form['productType']
        producto.region = request.form['region']
        producto.provincia = request.form['provincia']
        producto.canton = request.form.get('canton')
        producto.inicial_nombre = producto.nombre[0].upper() if producto.nombre else ''
        try:
            producto.precio = float(request.form.get('productPrice', 0) or 0)
        except ValueError:
            producto.precio = 0.0
        producto.unidad = request.form.get('productUnit')
        producto.descripcion = request.form.get('productDescription')
        try:
            producto.cantidad = float(request.form.get('productQuantity', 0) or 0)
        except ValueError:
            producto.cantidad = 0.0

        # Manejo de la imagen (opcional)
        imagen = request.files.get('productImage')
        if imagen and imagen.filename != '':
            filename = secure_filename(imagen.filename)
            uploads_dir = os.path.join(current_app.root_path, 'static', 'uploads')
            os.makedirs(uploads_dir, exist_ok=True)
            imagen.save(os.path.join(uploads_dir, filename))
            producto.imagen_url = filename

        db.session.commit()
        flash('Producto actualizado correctamente.', 'success')
        return redirect(url_for('perfil_agricultor'))

    # GET: mostrar formulario con los datos actuales
    return render_template('agricultor/editar_producto.html', producto=producto)

@app.route('/producto/eliminar/<int:producto_id>', methods=['POST', 'GET'])
def eliminar_producto(producto_id):
    """
    Elimina un producto del agricultor autenticado.
    - Métodos: POST, GET
    - Request: Ninguno
    - Response: Redirige a perfil_agricultor
    """
    producto = Producto.query.get_or_404(producto_id)
    # Opcional: verifica que el usuario sea el dueño del producto
    db.session.delete(producto)
    db.session.commit()
    flash('Producto eliminado correctamente.', 'success')
    return redirect(url_for('perfil_agricultor'))

# =================== Carrito de Compras ===================
# Agregar, eliminar, actualizar, confirmar y finalizar compras.
from app.models import Carrito, DetalleCarrito, Orden, OrdenItem
from flask_login import login_required, current_user

# --- Helper para obtener o crear carrito activo ---
def get_or_create_carrito(usuario_id):
    carrito = Carrito.query.filter_by(comprador_id=usuario_id, estado='activo').first()
    if not carrito:
        carrito = Carrito(comprador_id=usuario_id, estado='activo')
        db.session.add(carrito)
        db.session.commit()
    return carrito

# --- Agregar producto al carrito ---
@app.route('/agregar_al_carrito/<int:producto_id>', methods=['POST'])
@login_required
def agregar_al_carrito(producto_id):
    if current_user.user_type != 'comprador':
        flash('Solo los compradores pueden agregar al carrito.', 'warning')
        return redirect(url_for('productos'))
    cantidad = float(request.form.get('cantidad', 1))
    producto = Producto.query.get_or_404(producto_id)
    if producto.cantidad is not None and cantidad > producto.cantidad:
        flash('No hay suficiente stock disponible.', 'danger')
        return redirect(url_for('productos'))
    carrito = get_or_create_carrito(current_user.id)
    detalle = DetalleCarrito.query.filter_by(carrito_id=carrito.id, producto_id=producto_id).first()
    if detalle:
        detalle.cantidad += cantidad
    else:
        detalle = DetalleCarrito(carrito_id=carrito.id, producto_id=producto_id, cantidad=cantidad)
        db.session.add(detalle)
    db.session.commit()
    flash('Producto agregado al carrito.', 'success')
    return redirect(url_for('productos'))

# --- Eliminar producto del carrito ---
@app.route('/carrito/eliminar/<int:detalle_id>', methods=['POST'])
@login_required
def eliminar_del_carrito(detalle_id):
    detalle = DetalleCarrito.query.get_or_404(detalle_id)
    carrito = detalle.carrito
    if carrito.comprador_id != current_user.id:
        flash('No autorizado.', 'danger')
        return redirect(url_for('ver_carrito'))
    db.session.delete(detalle)
    db.session.commit()
    flash('Producto eliminado del carrito.', 'success')
    # Redirige a la página anterior si viene de confirmar_compra, si no, al carrito
    ref = request.referrer or ''
    if 'confirmar' in ref:
        return redirect(url_for('confirmar_compra'))
    return redirect(url_for('ver_carrito'))
@app.route('/carrito')
@login_required
def ver_carrito():
    if current_user.user_type != 'comprador':
        flash('Solo los compradores pueden ver el carrito.', 'warning')
        return redirect(url_for('productos'))
    carrito = Carrito.query.filter_by(comprador_id=current_user.id, estado='activo').first()
    items = []
    total = 0
    if carrito:
        # Solo incluir items cuyo producto existe
        items = [item for item in DetalleCarrito.query.filter_by(carrito_id=carrito.id).all() if item.producto is not None]
        total = sum(item.cantidad * (item.producto.precio or 0) for item in items)
    return render_template('carrito.html', items=items, total=total)

# --- API para obtener provincias únicas de productos en el carrito ---
@app.route('/api/carrito/provincias')
@login_required
def api_carrito_provincias():
    if current_user.user_type != 'comprador':
        return jsonify({'error': 'No autorizado'}), 403
    carrito = Carrito.query.filter_by(comprador_id=current_user.id, estado='activo').first()
    provincias = set()
    if carrito:
        detalles = DetalleCarrito.query.filter_by(carrito_id=carrito.id).all()
        for detalle in detalles:
            if detalle.producto and detalle.producto.provincia:
                provincias.add(detalle.producto.provincia)
    return jsonify({'provincias': list(provincias)})

# --- Actualizar cantidad/eliminar producto del carrito ---
@app.route('/carrito/actualizar', methods=['POST'])
@login_required
def actualizar_carrito():
    if current_user.user_type != 'comprador':
        flash('No autorizado.', 'danger')
        return redirect(url_for('productos'))
    carrito = Carrito.query.filter_by(comprador_id=current_user.id, estado='activo').first()
    if not carrito:
        flash('No hay carrito activo.', 'warning')
        return redirect(url_for('ver_carrito'))
    cambios = False

    # Procesa eliminaciones primero
    for key in request.form:
        if key.startswith('eliminar_'):
            detalle_id = int(key.replace('eliminar_', ''))
            detalle = DetalleCarrito.query.get(detalle_id)
            if detalle and detalle.carrito_id == carrito.id:
                db.session.delete(detalle)
                cambios = True

    # Luego procesa actualizaciones de cantidad
    for key, value in request.form.items():
        if key.startswith('cantidad_'):
            detalle_id = int(key.replace('cantidad_', ''))
            detalle = DetalleCarrito.query.get(detalle_id)
            if detalle and detalle.carrito_id == carrito.id:
                nueva_cantidad = float(value)
                if nueva_cantidad <= 0:
                    db.session.delete(detalle)
                    cambios = True
                elif detalle.cantidad != nueva_cantidad:
                    detalle.cantidad = nueva_cantidad
                    cambios = True

    if cambios:
        db.session.commit()
        flash('Carrito actualizado correctamente.', 'success')
    else:
        flash('No hubo cambios en el carrito.', 'info')
    ref = request.referrer or ''
    if 'confirmar' in ref:
        return redirect(url_for('confirmar_compra'))
    return redirect(url_for('ver_carrito'))

# --- Confirmar compra (pantalla de pago) ---
@app.route('/confirmar_compra')
@login_required
def confirmar_compra():
    if current_user.user_type != 'comprador':
        flash('No autorizado.', 'danger')
        return redirect(url_for('productos'))
    carrito = Carrito.query.filter_by(comprador_id=current_user.id, estado='activo').first()
    if not carrito or not carrito.detalles:
        flash('El carrito está vacío.', 'warning')
        return redirect(url_for('ver_carrito'))
    items = [item for item in DetalleCarrito.query.filter_by(carrito_id=carrito.id).all() if item.producto is not None]
    if not items:
        flash('El carrito está vacío o contiene productos eliminados.', 'warning')
        return redirect(url_for('ver_carrito'))
    total = sum(item.cantidad * (item.producto.precio or 0) for item in items)
    costo_envio = session.get('costo_envio', 0)
    total_final = total + costo_envio
    return render_template('confirmar_compra.html', items=items, total=total, costo_envio=costo_envio, total_final=total_final)

@app.route('/api/guardar_envio', methods=['POST'])
def guardar_envio():
    data = request.get_json()
    costo_envio = data.get('costo_envio')
    if costo_envio is not None:
        session['costo_envio'] = float(costo_envio)
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'No se recibió costo_envio'}), 400

# --- Finalizar compra (checkout) ---
@app.route('/carrito/finalizar', methods=['POST'])
@login_required
def finalizar_compra():
    if current_user.user_type != 'comprador':
        flash('No autorizado.', 'danger')
        return redirect(url_for('productos'))
    carrito = Carrito.query.filter_by(comprador_id=current_user.id, estado='activo').first()
    if not carrito or not carrito.detalles:
        flash('El carrito está vacío.', 'warning')
        return redirect(url_for('ver_carrito'))
    # Validar stock antes de crear la orden
    total = 0
    # Filtrar detalles cuyo producto no exista
    detalles_validos = [d for d in carrito.detalles if d.producto_id and Producto.query.get(d.producto_id)]
    if not detalles_validos:
        flash('No hay productos válidos en el carrito.', 'danger')
        return redirect(url_for('ver_carrito'))
    for detalle in detalles_validos:
        producto = Producto.query.get(detalle.producto_id)
        if producto.cantidad is not None and detalle.cantidad > producto.cantidad:
            flash(f'Sin stock suficiente para {producto.nombre}.', 'danger')
            return redirect(url_for('ver_carrito'))
        total += detalle.cantidad * (producto.precio or 0)
    # Obtener costo de envío de la sesión
    costo_envio = session.get('costo_envio', 0)
    # Crear la orden con costo de envío
    orden = Orden(comprador_id=current_user.id, total=total, costo_envio=costo_envio, estado='pendiente')
    db.session.add(orden)
    db.session.flush()
    for detalle in detalles_validos:
        producto = Producto.query.get(detalle.producto_id)
        if not producto:
            continue  # Seguridad extra, aunque ya filtramos
        producto.cantidad = (producto.cantidad or 0) - detalle.cantidad
        # Guardar snapshot de nombre y unidad
        orden_item = OrdenItem(
            orden_id=orden.id,
            producto_id=producto.id,
            cantidad=int(detalle.cantidad),
            precio_unitario=producto.precio or 0,
            producto_nombre=producto.nombre,
            producto_unidad=producto.unidad
        )
        db.session.add(orden_item)
        db.session.delete(detalle)
    carrito.estado = 'comprado'
    db.session.commit()
    # Crear viaje pendiente asociado a la orden
    from app.models import Viaje
    # Obtener primer producto y su agricultor
    primer_item = orden.items[0] if orden.items else None
    producto = primer_item.producto if primer_item else None
    agricultor = producto.usuario if producto else None
    origen = None
    if producto and agricultor:
        canton = producto.canton or ''
        provincia = producto.provincia or ''
        nombre_agricultor = agricultor.name or ''
        origen = f"{canton}, {provincia} — Agricultor: {nombre_agricultor}"
    else:
        origen = 'Sin datos de agricultor'

    # Obtener comprador
    comprador = orden.comprador_id
    comprador_usuario = None
    if comprador:
        from app.models import Usuario
        comprador_usuario = Usuario.query.get(comprador)
    destino = None
    if comprador_usuario:
        provincia = comprador_usuario.provincia or ''
        nombre_comprador = comprador_usuario.name or ''
        destino = f"{provincia} — Comprador: {nombre_comprador}"
    else:
        destino = 'Sin datos de comprador'

    viaje = Viaje(
        orden_id=orden.id,
        estado='pendiente',
        origen=origen,
        destino=destino,
    )
    db.session.add(viaje)
    db.session.commit()
    # Limpiar costo de envío de la sesión tras finalizar la compra
    session.pop('costo_envio', None)
    return render_template('compra_exitosa.html')

# =================== Página General de Productos ===================
# Página de exploración y filtros de productos.
@app.route('/productos')
def productos():
    region = request.args.get('region', '')
    provincia = request.args.get('provincia', '')
    tipo = request.args.get('tipo', '')
    nombre = request.args.get('nombre', '')
    precio_min = request.args.get('precio_min', type=float)
    precio_max = request.args.get('precio_max', type=float)
    query = Producto.query
    if region:
        query = query.filter_by(region=region)
    if provincia:
        query = query.filter_by(provincia=provincia)
    if tipo:
        query = query.filter_by(tipo=tipo)
    if nombre:
        query = query.filter(Producto.nombre.ilike(f"%{nombre}%"))
    if precio_min is not None:
        query = query.filter(Producto.precio >= precio_min)
    if precio_max is not None:
        query = query.filter(Producto.precio <= precio_max)
    productos = query.all()
    regiones = [r[0] for r in db.session.query(Producto.region).distinct().all()]
    provincias = [p[0] for p in db.session.query(Producto.provincia).distinct().all()]
    tipos = [t[0] for t in db.session.query(Producto.tipo).distinct().all()]

    favoritos_ids = []
    import logging
    favoritos_ids = []
    if current_user.is_authenticated and getattr(current_user, 'user_type', None) == 'comprador':
        # Forzar acceso a la relación del modelo para evitar shadowing
        try:
            favoritos_query = type(current_user).favoritos.__get__(current_user)
            favoritos_ids = [p.id for p in favoritos_query.all()]
        except Exception as e:
            logging.error(f"Error obteniendo favoritos: {e}, tipo: {type(current_user.favoritos)}")
            favoritos_ids = []
    return render_template('productos.html', productos=productos, regiones=regiones, provincias=provincias, tipos=tipos, user=current_user if current_user.is_authenticated else None, favoritos_ids=favoritos_ids )

# =================== APIs y Analítica ===================
# APIs para grafo, vistas, historial y ventas totales.
@app.route('/api/grafo_productos')
def api_grafo_productos():
    productos = Producto.query.all()
    G = nx.Graph()
    for p in productos:
        G.add_node(p.id, nombre=p.nombre, tipo=p.tipo, region=p.region, provincia=p.provincia, precio=p.precio, cantidad=p.cantidad, unidad=p.unidad)
    for i, p1 in enumerate(productos):
        for j, p2 in enumerate(productos):
            if i >= j:
                continue
            if p1.tipo == p2.tipo or p1.region == p2.region:
                G.add_edge(p1.id, p2.id)
    nodos = [
        {"id": n, **G.nodes[n]} for n in G.nodes
    ]
    aristas = [
        {"source": u, "target": v} for u, v in G.edges
    ]
    return jsonify({"nodes": nodos, "edges": aristas})

@app.route('/api/vistas_productos')
def api_vistas_productos():
    """
    Devuelve los datos de vistas por producto en formato JSON para el agricultor autenticado.
    - Método: GET
    - Response: JSON con lista de productos y sus vistas, tipo, precio, cantidad, unidad, provincia y región.
    """
    if 'user' not in session or session.get('user_type') != 'agricultor':
        return jsonify({'error': 'No autorizado'}), 403
    usuario = Usuario.query.filter_by(email=session['user']).first()
    productos = Producto.query.filter_by(usuario_id=usuario.id).all()
    data = {
        'productos': [
            {
                'nombre': p.nombre,
                'vistas': p.vistas or 0,
                'tipo': p.tipo,
                'precio': p.precio,
                'cantidad': p.cantidad,
                'unidad': p.unidad,
                'provincia': p.provincia,
                'region': p.region
            }
            for p in productos
        ]
    }
    return jsonify(data)

# =================== API de Ventas Totales ===================

@app.route('/api/historial_ventas')
@login_required
def api_historial_ventas():
    """
    Devuelve el historial de ventas del agricultor autenticado, ordenado por fecha/hora descendente.
    - Método: GET
    - Response: JSON con lista de ventas
    """
    if current_user.user_type != 'agricultor':
        return jsonify({'error': 'No autorizado'}), 403

    # Obtener productos del agricultor
    productos = Producto.query.filter_by(usuario_id=current_user.id).all()
    producto_ids = [p.id for p in productos]
    producto_map = {p.id: p.nombre for p in productos}

    # Obtener items de orden relacionados a estos productos
    orden_items = (
        OrdenItem.query
        .filter(OrdenItem.producto_id.in_(producto_ids))
        .join(Orden)
        .add_entity(Orden)
        .all()
    )

    from app.analytics_historial import preparar_historial_ventas
    historial = preparar_historial_ventas(orden_items, producto_map)
    return jsonify(historial)


@app.route('/api/ventas_totales')
@login_required
def api_ventas_totales():
    """
    Devuelve los datos de ventas totales y agregadas para el agricultor autenticado.
    - Método: GET
    - Response: JSON con agregados de ventas por producto, semana, mes y año.
    """
    if current_user.user_type != 'agricultor':
        return jsonify({'error': 'No autorizado'}), 403

    # Obtener todos los productos del agricultor
    productos = Producto.query.filter_by(usuario_id=current_user.id).all()
    producto_ids = [p.id for p in productos]
    producto_map = {p.id: p.nombre for p in productos}

    # Obtener todos los items de orden relacionados a estos productos
    orden_items = (
        OrdenItem.query
        .filter(OrdenItem.producto_id.in_(producto_ids))
        .join(Orden)
        .add_entity(Orden)
        .all()
    )

    # --- Lógica de agregación movida a analytics.py ---
    from app.analytics import calcular_ventas_agregadas
    data = calcular_ventas_agregadas(orden_items, producto_map)
    return jsonify(data)


# =================== API de Taxonomía ===================
# Endpoints para estructura, búsqueda, iconos, productos por subcategoría.

@app.route('/api/taxonomia')
def api_taxonomia():
    """
    Endpoint que devuelve la estructura simple de taxonomía de productos.
    - Método: GET
    - Response: JSON con estructura simple {categoria: {subcategoria: [productos]}}
    """
    from app.taxonomia import obtener_estructura_simple
    return jsonify(obtener_estructura_simple())

@app.route('/api/taxonomia/estructura')
def api_taxonomia_estructura():
    """
    Endpoint para el widget de árbol de clasificación de productos.
    - Método: GET
    - Response: JSON con la estructura adecuada para el widget (categoría > subcategoría > productos)
    """
    from app.taxonomia import obtener_estructura_taxonomia
    return jsonify(obtener_estructura_taxonomia())




@app.route('/api/taxonomia/buscar')
def api_buscar_productos():
    """
    Endpoint para búsqueda de productos en la taxonomía.
    - Método: GET
    - Query params: q (término de búsqueda)
    - Response: JSON con lista de productos que coinciden
    """
    from app.taxonomia import buscar_productos
    termino = request.args.get('q', '')
    
    if len(termino) < 2:
        return jsonify([])
    
    resultados = buscar_productos(termino)
    # Convertir al formato esperado por el frontend
    resultados_formato = []
    for resultado in resultados:
        resultados_formato.append({
            "producto": resultado["nombre"],
            "categoria": resultado["categoria"],
            "subcategoria": resultado["subcategoria"]
        })
    
    return jsonify(resultados_formato)

# Agregar ruta para obtener íconos
@app.route('/api/taxonomia/iconos')
def api_iconos_categorias():
    """
    Endpoint que devuelve los íconos de las categorías principales.
    - Método: GET
    - Response: JSON con íconos {categoria: icono}
    """
    from app.taxonomia import obtener_iconos_categorias
    return jsonify(obtener_iconos_categorias())

# Agregar ruta para obtener productos por subcategoría
@app.route('/api/productos_por_subcategoria/<int:subcat_id>')
def api_productos_por_subcategoria(subcat_id):
    """
    Endpoint que devuelve los productos de una subcategoría específica.
    - Método: GET
    - Response: JSON con lista de productos de la subcategoría
    """
    from app.models import Producto
    productos = Producto.query.filter_by(subcategoria_id=subcat_id).all()
    return jsonify([{'id': p.id, 'nombre': p.nombre} for p in productos])

# =================== Utilidades y Context Processors ===================
# Inyección de contexto, endpoints auxiliares, pruebas.

@app.context_processor
def inject_user():
    """
    Inyecta el usuario y tipo de usuario en el contexto de las plantillas.
    Si usas Flask-Login, prioriza current_user.
    """
    from flask_login import current_user
    if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
        return {
            'user': current_user,
            'user_type': getattr(current_user, 'user_type', None)
        }
    return {
        'user': session.get('user'),
        'user_type': session.get('user_type')
    }

# Endpoint para obtener subcategorías de una categoría
@app.route('/api/subcategorias/<int:categoria_id>')
def api_subcategorias(categoria_id):
    from app.models import Subcategoria
    subcategorias = Subcategoria.query.filter_by(categoria_id=categoria_id).order_by(Subcategoria.nombre).all()
    return jsonify([{'id': s.id, 'nombre': s.nombre} for s in subcategorias])