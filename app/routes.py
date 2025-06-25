# =================== Importaciones estándar ===================
import os  # Para interactuar con el sistema operativo: manejo de rutas de archivos y variables de entorno.
from datetime import datetime  # Para trabajar con fechas y horas (e.g., creación de órdenes, timestamps).
import requests  # Para realizar peticiones HTTP a APIs externas (como la del chatbot).
import networkx as nx  # Librería para la creación, manipulación y estudio de grafos complejos.
import pandas as pd  # Para análisis y manipulación de datos, especialmente en los módulos de analytics.

# =================== Importaciones de terceros (Framework y Extensiones) ===================
from flask import (
    render_template,  # Para renderizar plantillas HTML.
    request,          # Para acceder a los datos de las peticiones entrantes (formularios, JSON).
    redirect,         # Para redirigir al usuario a otra URL.
    url_for,          # Para construir URLs para las rutas de la aplicación.
    flash,            # Para mostrar mensajes temporales al usuario (e.g., 'Login exitoso').
    session,          # Para almacenar datos de la sesión del usuario.
    send_file,        # Para enviar archivos estáticos desde el servidor.
    jsonify,          # Para convertir objetos de Python a formato JSON para las respuestas de la API.
    current_app       # Proxy al objeto de la aplicación actual.
)
from flask_login import current_user, login_required, login_user  # Para gestionar la autenticación y sesiones de usuario.
from flask_mail import Message  # Para crear objetos de mensaje para el envío de correos.
from werkzeug.security import generate_password_hash, check_password_hash  # Para hashear y verificar contraseñas de forma segura.
from werkzeug.utils import secure_filename  # Para asegurar que los nombres de archivo subidos sean seguros.
from dotenv import load_dotenv  # Para cargar variables de entorno desde un archivo .env.

# =================== Importaciones locales (Módulos de AgroGrid) ===================
from app import app, mail, db  # Importa la instancia de la app, de mail y de la BD desde el paquete principal.
from app.models import (  # Importa todos los modelos de la base de datos para interactuar con ellos.
    Usuario, Producto, Categoria, Subcategoria, Carrito, Vehiculo,
    Testimonio, Orden, DetalleCarrito, OrdenItem, Viaje
)
from app.token_utils import generate_token, confirm_token  # Utilidades para generar y confirmar tokens (e.g., para reset de contraseña).
from app.grafo_transporte import grafo_cantonal, dijkstra  # El grafo de transporte y el algoritmo para calcular rutas.
from app.ubicacion import obtener_estructura_ubicacion  # Lógica para obtener la jerarquía de ubicaciones.
from app.taxonomia import obtener_taxonomia_catalogo  # Lógica para obtener la jerarquía de categorías de productos.
from app.analytics import calcular_ventas_agregadas  # Funciones para realizar análisis de datos de ventas.
from app.chatbot_prompts import SYSTEM_PROMPT_AGROGRID, MAX_TOKENS_DEFAULT  # Constantes y prompts para el chatbot.
from app.chatbot_knowledge import buscar_respuesta_concreta  # Lógica para buscar en la base de conocimiento del chatbot.

# =================== Rutas y lógica ===================

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


@app.route('/centro_ayuda')
def centro_ayuda():
    user = current_user if current_user.is_authenticated else None
    user_type = getattr(current_user, 'user_type', None) if current_user.is_authenticated else None
    return render_template('centro_ayuda.html', user=user, user_type=user_type)

@app.route('/blog')
def blog():
    user = current_user if current_user.is_authenticated else None
    user_type = getattr(current_user, 'user_type', None) if current_user.is_authenticated else None
    return render_template('blog.html', user=user, user_type=user_type)

@app.route('/faq')
def faq():
    user = current_user if current_user.is_authenticated else None
    user_type = getattr(current_user, 'user_type', None) if current_user.is_authenticated else None
    return render_template('faq.html', user=user, user_type=user_type)

@app.route('/testimonios')
def testimonios():
    from app.models import Testimonio
    todos_los_testimonios = Testimonio.query.order_by(Testimonio.fecha_creacion.desc()).all()
    user = current_user if current_user.is_authenticated else None
    user_type = getattr(current_user, 'user_type', None) if current_user.is_authenticated else None
    return render_template('testimonios.html', user=user, user_type=user_type, testimonios=todos_los_testimonios)

@app.route('/noticias')
def noticias():
    user = current_user if current_user.is_authenticated else None
    user_type = getattr(current_user, 'user_type', None) if current_user.is_authenticated else None
    return render_template('noticias.html', user=user, user_type=user_type)

@app.route('/comprador/calificar_pedido/<int:pedido_id>', methods=['GET', 'POST'])
@login_required
def calificar_pedido(pedido_id):
    pedido = Orden.query.get_or_404(pedido_id)
    puede_calificar = False
    calificacion_actual = None
    # Solo el comprador dueño y entregado puede calificar (usando el estado real del viaje)
    viaje = getattr(pedido, 'viaje', None)
    estado_viaje = viaje.estado if viaje else pedido.estado
    # Inicializar transportista y vehiculo como None para evitar UnboundLocalError
    transportista = None
    vehiculo = None
    # Obtener datos del transportista y vehículo (si existen)
    if viaje and viaje.transportista:
        transportista = {
            'nombre': viaje.transportista.name,
            'email': viaje.transportista.email,
            'telefono': viaje.transportista.phone
        }
    if viaje and hasattr(viaje, 'vehiculo') and viaje.vehiculo:
        vehiculo = viaje.vehiculo
    else:
        # Fallback: buscar vehículo por transportista si es único
        if viaje and viaje.transportista_id:
            from app.models import Vehiculo
            vehiculos = Vehiculo.query.filter_by(transportista_id=viaje.transportista_id).all()
            if len(vehiculos) == 1:
                vehiculo = vehiculos[0]
    calificacion_actual = pedido.calificacion if hasattr(pedido, 'calificacion') else None
    # Solo el comprador dueño y entregado puede calificar, y solo si no ha calificado antes
    if pedido.comprador_id == current_user.id and estado_viaje == 'entregado' and not calificacion_actual:
        puede_calificar = True
        if request.method == 'POST':
            # Relee desde la base por seguridad
            pedido_actual = Orden.query.get(pedido.id)
            if pedido_actual.calificacion is not None:
                flash('Este pedido ya fue calificado. No puedes calificar nuevamente.', 'warning')
                return redirect(url_for('calificar_pedido', pedido_id=pedido.id))
            calif = request.form.get('calificacion', type=int)
            if calif and 1 <= calif <= 5:
                pedido_actual.calificacion = calif
                if viaje:
                    viaje.calificacion = calif
                db.session.commit()
                flash('¡Gracias por tu calificación!', 'success')
                return redirect(url_for('perfil_comprador'))
            else:
                flash('Selecciona una calificación válida.', 'warning')
    else:
        puede_calificar = False
    # Pasar el estado real del viaje al template
    return render_template('comprador/calificar_pedido.html', pedido=pedido, puede_calificar=puede_calificar, calificacion_actual=calificacion_actual, transportista=transportista, vehiculo=vehiculo, estado_real=estado_viaje)
    # Obtener datos del transportista y vehículo (si existen)
    viaje = getattr(pedido, 'viaje', None)
    transportista = None
    vehiculo = None
    if viaje and viaje.transportista:
        transportista = {
            'nombre': viaje.transportista.name,
            'email': viaje.transportista.email,
            'telefono': viaje.transportista.phone
        }
    if viaje and hasattr(viaje, 'vehiculo') and viaje.vehiculo:
        vehiculo = viaje.vehiculo
    else:
        # Fallback: buscar vehículo por transportista si es único
        if transportista:
            from app.models import Vehiculo
            vehiculos = Vehiculo.query.filter_by(transportista_id=viaje.transportista_id).all()
            if len(vehiculos) == 1:
                vehiculo = vehiculos[0]
    return render_template('comprador/calificar_pedido.html', pedido=pedido, puede_calificar=puede_calificar, calificacion_actual=calificacion_actual, transportista=transportista, vehiculo=vehiculo)


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
    from app.models import Testimonio
    testimonios = Testimonio.query.order_by(Testimonio.fecha_creacion.desc()).limit(6).all()
    user = current_user if current_user.is_authenticated else None
    user_type = getattr(current_user, 'user_type', None) if current_user.is_authenticated else None
    return render_template('index.html', user=user, user_type=user_type, testimonios=testimonios)

@app.route('/eliminar_testimonio/<int:testimonio_id>', methods=['POST'])
def eliminar_testimonio(testimonio_id):
    from app.models import Testimonio
    t = Testimonio.query.get(testimonio_id)
    if t:
        db.session.delete(t)
        db.session.commit()
        flash('Testimonio eliminado.', 'success')
    else:
        flash('Testimonio no encontrado.', 'danger')
    return redirect(url_for('testimonios'))

@app.route('/eliminar_todos_testimonios', methods=['POST'])
def eliminar_todos_testimonios():
    from app.models import Testimonio
    Testimonio.query.delete()
    db.session.commit()
    flash('Todos los testimonios han sido eliminados.', 'success')
    return redirect(url_for('testimonios'))

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

    # Solo para la sección de Total General: datos para gráfica agrupada por semana, mes y día
    def make_barplot_series(dic):
        if not dic:
            return {'labels': [], 'data': []}
        keys = list(dic.keys())
        vals = list(dic.values())
        return {'labels': keys, 'data': vals}

    # Día: agregar agrupación diaria
    df = None
    try:
        from app.analytics import calcular_ventas_agregadas
        # Reutilizar ventas_totales_data ya calculado
        if 'ventas_totales_data' in locals():
            df = ventas_totales_data.get('df')
        if df is None:
            # reconstruir df si no existe
            orden_items = (
                db.session.query(OrdenItem, Orden)
                .join(Orden, OrdenItem.orden_id == Orden.id)
                .filter(OrdenItem.producto_id.in_(producto_ids))
                .all()
            )
            fechas = []
            totales = []
            for item, orden in orden_items:
                fechas.append(orden.creado_en)
                totales.append(item.cantidad * item.precio_unitario)
            df = pd.DataFrame({'fecha': fechas, 'total': totales})
        df['dia'] = df['fecha'].dt.strftime('%Y-%m-%d')
        por_dia = df.groupby('dia')['total'].sum().to_dict()
    except Exception:
        por_dia = {}

    ventas_totales_series = {
        'semana': make_barplot_series(ventas_totales_data.get('por_semana')),
        'mes': make_barplot_series(ventas_totales_data.get('por_mes')),
        'dia': make_barplot_series(por_dia),
        'anio': make_barplot_series(ventas_totales_data.get('por_anio')),
    }

    return render_template('agricultor/perfil_agricultor.html',
                           user=usuario,
                           productos=productos_del_agricultor,
                           ventas=ventas,
                           ventas_totales=ventas_totales_calculadas,
                           numero_productos=numero_productos_publicados,
                           vistas_productos=vistas_a_productos,
                           user_type=session['user_type'],
                           ventas_totales_series=ventas_totales_series)

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
            'id': pedido.id,
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

    # --- AGREGACIÓN DE COMPRAS PARA PANEL ---
    # Preparar lista de (OrdenItem, Orden) para todas las órdenes del comprador
    orden_items = []
    producto_map = {}
    for pedido in pedidos:
        items = OrdenItem.query.filter_by(orden_id=pedido.id).all()
        for item in items:
            orden_items.append((item, pedido))
            # Mapear producto_id a nombre (si existe)
            if item.producto_id and item.producto_id not in producto_map:
                producto = Producto.query.get(item.producto_id)
                if producto:
                    producto_map[item.producto_id] = producto.nombre
    from app.analytics import calcular_compras_agregadas
    compras_agregadas = calcular_compras_agregadas(orden_items, producto_map)

    # Prepara listas top 5 para el template (ordenadas)
    top_5_gasto = sorted(compras_agregadas['por_producto_gasto'].items(), key=lambda x: x[1], reverse=True)[:5]
    top_5_cantidad = sorted(compras_agregadas['por_producto_cantidad'].items(), key=lambda x: x[1], reverse=True)[:5]

    return render_template('comprador/perfil_comprador.html',
                           user=usuario,
                           user_type=session['user_type'],
                           pedidos=pedidos_lista,
                           favoritos=favoritos,
                           favoritos_count=favoritos_count,
                           pedidos_realizados=pedidos_realizados,
                           compras_agregadas=compras_agregadas,
                           top_5_gasto=top_5_gasto,
                           top_5_cantidad=top_5_cantidad)

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
    vehiculos = Vehiculo.query.filter_by(transportista_id=usuario.id).all() if usuario else []
    # Calcular promedio de calificaciones de viajes entregados
    from app.models import Viaje
    viajes_entregados = Viaje.query.filter_by(transportista_id=usuario.id, estado='entregado').all() if usuario else []
    calificaciones = [v.calificacion for v in viajes_entregados if v.calificacion is not None]
    if calificaciones:
        promedio = round(sum(calificaciones)/len(calificaciones), 2)
    else:
        promedio = 'N/A'
    from app.analytics import generar_barplot_envios_entregados, numpy_agrupa_entregas_por_periodo, numpy_agrupa_ganancias_por_periodo
    fechas_entrega = [v.fecha_entrega for v in viajes_entregados if v.fecha_entrega]
    barplot_filename = generar_barplot_envios_entregados(fechas_entrega)
    barplot_envios_url = url_for('static', filename=barplot_filename)
    # Calcula los datos para el JS interactivo
    from datetime import datetime, timedelta
    now = datetime.utcnow()
    semana = sum(1 for f in fechas_entrega if f >= now - timedelta(days=7))
    mes = sum(1 for f in fechas_entrega if f >= now - timedelta(days=30))
    anio = sum(1 for f in fechas_entrega if f >= now - timedelta(days=365))
    total = len(fechas_entrega)
    barplot_data = {'Semana': semana, 'Mes': mes, 'Año': anio, 'Total': total}

    # Series temporales para gráfico interactivo de entregas
    etiquetas_sem, datos_sem = numpy_agrupa_entregas_por_periodo(fechas_entrega, 'semana', 12)
    etiquetas_mes, datos_mes = numpy_agrupa_entregas_por_periodo(fechas_entrega, 'mes', 12)
    etiquetas_ano, datos_ano = numpy_agrupa_entregas_por_periodo(fechas_entrega, 'año', 12)
    barplot_series = {
        'semana': {'labels': etiquetas_sem, 'data': datos_sem},
        'mes': {'labels': etiquetas_mes, 'data': datos_mes},
        'año': {'labels': etiquetas_ano, 'data': datos_ano}
    }

    # Series temporales para gráfico de ganancias
    # Si el campo costo está vacío, intenta obtenerlo desde la orden asociada
    fechas_y_montos = []
    for v in viajes_entregados:
        if v.fecha_entrega:
            monto = v.costo
            if monto is None and hasattr(v, 'orden') and v.orden:
                # Prioriza costo_envio, si no existe usa total
                monto = getattr(v.orden, 'costo_envio', None)
                if monto is None:
                    monto = getattr(v.orden, 'total', None)
            if monto is not None:
                fechas_y_montos.append((v.fecha_entrega, monto))
    et_sem_g, dat_sem_g = numpy_agrupa_ganancias_por_periodo(fechas_y_montos, 'semana', 12)
    et_mes_g, dat_mes_g = numpy_agrupa_ganancias_por_periodo(fechas_y_montos, 'mes', 12)
    et_ano_g, dat_ano_g = numpy_agrupa_ganancias_por_periodo(fechas_y_montos, 'año', 12)
    barplot_ganancias_series = {
        'semana': {'labels': et_sem_g, 'data': dat_sem_g},
        'mes': {'labels': et_mes_g, 'data': dat_mes_g},
        'año': {'labels': et_ano_g, 'data': dat_ano_g}
    }

    envios_realizados = len(viajes_entregados)
    return render_template('transportista/perfil_transportista.html',
                           user=usuario,
                           user_type=session['user_type'],
                           vehiculos=vehiculos,
                           calificacion=promedio,
                           envios_realizados=envios_realizados,
                           barplot_envios_url=barplot_envios_url,
                           barplot_data=barplot_data,
                           barplot_series=barplot_series,
                           barplot_ganancias_series=barplot_ganancias_series or {})

# --- Eliminar vehículo ---
@app.route('/perfil/transportista/vehiculo/<int:vehiculo_id>/eliminar', methods=['POST'])
@login_required
def eliminar_vehiculo(vehiculo_id):
    vehiculo = Vehiculo.query.get_or_404(vehiculo_id)
    if current_user.user_type != 'transportista' or vehiculo.transportista_id != current_user.id:
        flash('No autorizado para eliminar este vehículo.', 'danger')
        return redirect(url_for('perfil_transportista'))
    # Eliminar imagen si existe
    if vehiculo.imagen_url:
        import os
        img_path = os.path.join(current_app.root_path, 'static', vehiculo.imagen_url)
        if os.path.exists(img_path):
            try:
                os.remove(img_path)
            except Exception:
                pass
    db.session.delete(vehiculo)
    db.session.commit()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True})
    flash('Vehículo eliminado correctamente.', 'success')
    return redirect(url_for('perfil_transportista'))

# --- Registro de vehículo ---
@app.route('/perfil/transportista/vehiculo/agregar', methods=['POST'])
@login_required
def agregar_vehiculo():
    if current_user.user_type != 'transportista':
        flash('No autorizado.', 'danger')
        return redirect(url_for('perfil_transportista'))
    placa = request.form.get('placa', '').strip().upper()
    tipo = request.form.get('tipo', '').strip()
    capacidad = request.form.get('capacidad', '').strip()
    descripcion = request.form.get('descripcion', '').strip()
    imagen_url = None
    # Manejo de imagen
    imagen = request.files.get('imagen')
    if imagen and imagen.filename:
        from werkzeug.utils import secure_filename
        filename = secure_filename(imagen.filename)
        uploads_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'vehiculos')
        os.makedirs(uploads_dir, exist_ok=True)
        filepath = os.path.join(uploads_dir, filename)
        imagen.save(filepath)
        imagen_url = f"uploads/vehiculos/{filename}"
    if not placa or not tipo:
        flash('La placa y el tipo son obligatorios.', 'warning')
        return redirect(url_for('perfil_transportista'))
    # Validar placa única por transportista
    existe = Vehiculo.query.filter_by(transportista_id=current_user.id, placa=placa).first()
    if existe:
        flash('Ya has registrado un vehículo con esa placa.', 'warning')
        return redirect(url_for('perfil_transportista'))
    vehiculo = Vehiculo(
        transportista_id=current_user.id,
        placa=placa,
        tipo=tipo,
        capacidad=capacidad,
        descripcion=descripcion,
        imagen_url=imagen_url
    )
    db.session.add(vehiculo)
    db.session.commit()
    flash('Vehículo registrado correctamente.', 'success')
    return redirect(url_for('perfil_transportista'))

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
        # Determinar valor_envio
        valor_envio = v.costo
        if valor_envio is None and orden:
            valor_envio = getattr(orden, 'costo_envio', None)
            if valor_envio is None:
                valor_envio = getattr(orden, 'total', None)
        resultado.append({
            'id': v.id,
            'origen': v.origen or '',
            'destino': v.destino or '',
            'productos': ', '.join(productos),
            'agricultor': agricultor or '',
            'comprador': comprador_nombre,
            'valor_envio': valor_envio
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
        # Determinar valor_envio
        valor_envio = v.costo
        if valor_envio is None and orden:
            valor_envio = getattr(orden, 'costo_envio', None)
            if valor_envio is None:
                valor_envio = getattr(orden, 'total', None)
        resultado.append({
            'id': v.id,
            'origen': v.origen or '',
            'destino': v.destino or '',
            'productos': ', '.join(productos),
            'estado': v.estado,
            'valor_envio': valor_envio
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
    return render_template(
        'confirmar_compra.html',
        items=items,
        total=total,
        costo_envio=costo_envio,
        total_final=total_final
    )

@app.route('/api/guardar_envio', methods=['POST'])
def guardar_envio():
    data = request.get_json()
    costo_envio = data.get('costo_envio')
    if costo_envio is not None:
        session['costo_envio'] = float(costo_envio)
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'No se recibió costo_envio'}), 400

# --- Login admin ---
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        user = request.form.get('user')
        pw = request.form.get('password')
        if user == 'admin' and pw == 'admin123':
            session['is_admin'] = True
            return redirect(url_for('admin_panel'))
        else:
            flash('Credenciales incorrectas', 'danger')
    return render_template('admin_login.html')

# --- Benchmark Sorts solo para admin ---
@app.route('/admin/panel', methods=['GET', 'POST'])
def admin_panel():
    if not session.get('is_admin'):
        return redirect(url_for('admin_login'))
    from app.models import Orden
    from app.utils.sorting import benchmark_sorts
    from app.analytics import numpy_agrupa_ganancias_por_periodo
    import random

    # --- DATOS REALES PARA BENCHMARK ---
    benchmark_tipo = request.form.get('benchmark_tipo') if request.method == 'POST' else request.args.get('benchmark_tipo', 'montos')
    lista_raw = request.form.get('lista', '') if request.method == 'POST' else ''
    lista_real = []
    tipo_dato = 'numeros'
    if benchmark_tipo == 'productos':
        productos = Producto.query.order_by(Producto.nombre).all()
        lista_real = [p.nombre for p in productos]
        tipo_dato = 'productos'
    elif benchmark_tipo == 'usuarios':
        usuarios = Usuario.query.order_by(Usuario.name).all()
        lista_real = [u.name for u in usuarios]
        tipo_dato = 'usuarios'
    else:
        ordenes = Orden.query.filter(Orden.estado.in_(['entregado', 'pagado', 'finalizado'])).all()
        lista_real = [float(o.total) for o in ordenes if o.total is not None]
        tipo_dato = 'numeros'
    # Si el usuario ingresó una lista manual, úsala
    if lista_raw:
        try:
            if tipo_dato == 'numeros':
                lista = [float(x.strip()) for x in lista_raw.split(',') if x.strip()]
            else:
                lista = [x.strip() for x in lista_raw.split(',') if x.strip()]
        except Exception:
            lista = lista_real
    else:
        lista = lista_real
    if len(lista) < 2:
        lista = [random.randint(10, 100) for _ in range(10)]
        tipo_dato = 'numeros'
    results = benchmark_sorts(lista, tipo_dato=tipo_dato)
    lista_real_str = ', '.join(str(x) for x in lista)

    # --- GRÁFICAS DE VENTAS Y GANANCIAS ---
    # Agrupa ventas por periodo usando fechas y montos de las órdenes
    fechas_y_montos = [(o.creado_en, float(o.total)) for o in ordenes if o.creado_en and o.total is not None]
    labels_mes, ventas_mes = numpy_agrupa_ganancias_por_periodo(fechas_y_montos, 'mes', 12)
    labels_sem, ventas_sem = numpy_agrupa_ganancias_por_periodo(fechas_y_montos, 'semana', 12)
    labels_anio, ventas_anio = numpy_agrupa_ganancias_por_periodo(fechas_y_montos, 'año', 12)
    # Ganancias: 1% de las ventas
    ganancias_mes = [round(v*0.01, 2) for v in ventas_mes]
    ganancias_sem = [round(v*0.01, 2) for v in ventas_sem]
    ganancias_anio = [round(v*0.01, 2) for v in ventas_anio]
    ventas_series = {
        'mes': {'labels': labels_mes, 'ventas': ventas_mes, 'ganancias': ganancias_mes},
        'semana': {'labels': labels_sem, 'ventas': ventas_sem, 'ganancias': ganancias_sem},
        'año': {'labels': labels_anio, 'ventas': ventas_anio, 'ganancias': ganancias_anio},
    }
    # --- KPIs ---
    # Ventas y ganancias: usa la lista real de montos de órdenes
    if benchmark_tipo == 'montos' or tipo_dato == 'numeros':
        ventas_lista = [x for x in lista_real if isinstance(x, (int, float))]
        kpi_ventas = round(sum(ventas_lista), 2)
        kpi_ordenes = len(ventas_lista)
    else:
        # Si está en benchmark de productos/usuarios, calcula ventas y órdenes directamente
        ordenes_total = Orden.query.filter(Orden.estado.in_(['entregado', 'pagado', 'finalizado'])).all()
        kpi_ventas = round(sum([float(o.total) for o in ordenes_total if o.total is not None]), 2)
        kpi_ordenes = len(ordenes_total)
    kpi_ganancias = round(kpi_ventas * 0.01, 2)
    from app.models import Usuario, Producto
    kpi_usuarios = Usuario.query.count()
    kpi_productos = Producto.query.count()

    # --- Actividad reciente ---
    # Últimas 5 órdenes
    ult_ordenes = Orden.query.order_by(Orden.creado_en.desc()).limit(5).all()
    ult_usuarios = Usuario.query.order_by(Usuario.id.desc()).limit(5).all()
    ult_productos = Producto.query.order_by(Producto.id.desc()).limit(5).all()
    actividad_reciente = []
    for o in ult_ordenes:
        actividad_reciente.append({
            'fecha': o.creado_en.strftime('%Y-%m-%d %H:%M'),
            'tipo': 'Nueva orden',
            'usuario': o.comprador_id,
            'detalle': f'Total: ${o.total:.2f}'
        })
    for u in ult_usuarios:
        actividad_reciente.append({
            'fecha': u.id,  # Debería ser fecha de registro si está disponible
            'tipo': 'Nuevo usuario',
            'usuario': u.name,
            'detalle': u.email
        })
    for p in ult_productos:
        actividad_reciente.append({
            'fecha': p.id,  # Debería ser fecha de alta si está disponible
            'tipo': 'Nuevo producto',
            'usuario': getattr(p.usuario, 'name', 'N/A'),
            'detalle': p.nombre
        })
    actividad_reciente = sorted(actividad_reciente, key=lambda x: str(x['fecha']), reverse=True)[:10]

    # Usar la lista mostrada en el input (manual o real)
    lista_raw_final = lista_raw if lista_raw else ','.join(str(x) for x in lista)
    return render_template(
        'admin_panel.html',
        results=results,
        lista_raw=lista_raw_final,
        ventas_series=ventas_series,
        kpi_ventas=kpi_ventas,
        kpi_ganancias=kpi_ganancias,
        kpi_ordenes=kpi_ordenes,
        kpi_usuarios=kpi_usuarios,
        kpi_productos=kpi_productos,
        actividad_reciente=actividad_reciente
    )

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
    from app.utils.sorting import quicksort, mergesort
    from app.models import OrdenItem, Orden
    import logging
    region = request.args.get('region', '')
    provincia = request.args.get('provincia', '')
    tipo = request.args.get('tipo', '')
    nombre = request.args.get('nombre', '')
    precio_min = request.args.get('precio_min', type=float)
    precio_max = request.args.get('precio_max', type=float)
    sort = request.args.get('sort', 'recent')  # 'sold', 'viewed', 'recent'
    sort_algo = request.args.get('sort_algo', 'quicksort')  # 'quicksort', 'mergesort'

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

    # --- Sorting  ---
    def sort_products(productos, sort, sort_algo):
        if sort == 'sold':
            producto_ids = [p.id for p in productos]
            ventas = {pid: 0 for pid in producto_ids}
            orden_items = (
                OrdenItem.query.filter(OrdenItem.producto_id.in_(producto_ids))
                .all()
            )
            for item in orden_items:
                ventas[item.producto_id] += item.cantidad
           
            productos_with_sales = [(p, ventas.get(p.id, 0)) for p in productos]
            
            key_fn = lambda x: -x[1]
            arr = productos_with_sales
            if sort_algo == 'mergesort':
                sorted_arr = mergesort(arr, key=key_fn)
            else:
                sorted_arr = quicksort(arr, key=key_fn)
            productos_sorted = [p for p, _ in sorted_arr]
            return productos_sorted
        elif sort == 'viewed':
            arr = productos[:]
            key_fn = lambda p: -(getattr(p, 'vistas', 0) or 0)
            if sort_algo == 'mergesort':
                arr = mergesort(arr, key=key_fn)
            else:
                arr = quicksort(arr, key=key_fn)
            return arr
        else:  
            arr = productos[:]
            key_fn = lambda p: -(getattr(p, 'id', 0) or 0)  
            if sort_algo == 'mergesort':
                arr = mergesort(arr, key=key_fn)
            else:
                arr = quicksort(arr, key=key_fn)
            return arr

    import time
    sort_time = 0
    t0 = time.time()
    productos = sort_products(productos, sort, sort_algo)
    sort_time = (time.time() - t0) * 1000  # ms

    regiones = [r[0] for r in db.session.query(Producto.region).distinct().all()]
    provincias = [p[0] for p in db.session.query(Producto.provincia).distinct().all()]
    tipos = [t[0] for t in db.session.query(Producto.tipo).distinct().all()]

    favoritos_ids = []
    recomendados = []
    if current_user.is_authenticated and getattr(current_user, 'user_type', None) == 'comprador':
        # Forzar acceso a la relación del modelo para evitar shadowing
        try:
            favoritos_query = type(current_user).favoritos.__get__(current_user)
            favoritos_ids = [p.id for p in favoritos_query.all()]
        except Exception as e:
            logging.error(f"Error obteniendo favoritos: {e}, tipo: {type(current_user.favoritos)}")
            favoritos_ids = []
        # Usar lógica de recomendación separada
        from app.utils.recomendador import recomendar_productos_para_usuario
        recomendados = recomendar_productos_para_usuario(current_user.id, max_n=10)
    return render_template(
        'productos.html',
        productos=productos,
        regiones=regiones,
        provincias=provincias,
        tipos=tipos,
        user=current_user if current_user.is_authenticated else None,
        favoritos_ids=favoritos_ids,
        recomendados=recomendados,
        sort=sort,
        sort_algo=sort_algo,
        sort_time=sort_time
    )

# =================== APIs y Analítica ===================

@app.route('/api/ganancias_transportista')
@login_required
def api_ganancias_transportista():
    if current_user.user_type != 'transportista':
        return jsonify({'error': 'No autorizado'}), 403
    from app.models import Viaje
    from app.analytics import numpy_agrupa_ganancias_por_periodo
    usuario = current_user
    viajes_entregados = Viaje.query.filter_by(transportista_id=usuario.id, estado='entregado').all()
    fechas_y_montos = []
    for v in viajes_entregados:
        if v.fecha_entrega:
            monto = v.costo
            if monto is None and hasattr(v, 'orden') and v.orden:
                monto = getattr(v.orden, 'costo_envio', None)
                if monto is None:
                    monto = getattr(v.orden, 'total', None)
            if monto is not None:
                fechas_y_montos.append((v.fecha_entrega, monto))
    et_sem_g, dat_sem_g = numpy_agrupa_ganancias_por_periodo(fechas_y_montos, 'semana', 12)
    et_mes_g, dat_mes_g = numpy_agrupa_ganancias_por_periodo(fechas_y_montos, 'mes', 12)
    et_ano_g, dat_ano_g = numpy_agrupa_ganancias_por_periodo(fechas_y_montos, 'año', 12)
    return jsonify({
        'semana': {'labels': et_sem_g, 'data': dat_sem_g},
        'mes': {'labels': et_mes_g, 'data': dat_mes_g},
        'año': {'labels': et_ano_g, 'data': dat_ano_g}
    })

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

# =================== Chatbot Gridi ===================

# Cargar variables de entorno (.env)
load_dotenv()

@app.route('/chatbot', methods=['POST'])
def chatbot():
    """
    Endpoint para el chatbot Gridi usando la API de DeepSeek (tipo OpenAI compatible).
    Recibe un mensaje del usuario, consulta DeepSeek y devuelve la respuesta generada.
    """
    data = request.get_json()
    user_message = data.get('message', '')
    if not user_message:
        return jsonify({'response': 'Por favor, escribe tu pregunta.'}), 400

    # Primero busca una respuesta concreta en la base de conocimientos
    respuesta_concreta = buscar_respuesta_concreta(user_message)
    if respuesta_concreta:
        return jsonify({'response': respuesta_concreta})

    # Configuración DeepSeek
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        return jsonify({'response': 'No se encontró la API key de DeepSeek en el entorno.'}), 500

    url = 'https://api.deepseek.com/v1/chat/completions'  
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    payload = {
        "model": "deepseek-chat",  
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT_AGROGRID + " Responde SIEMPRE en español"
            },
            {"role": "user", "content": user_message}
        ],
        "max_tokens": MAX_TOKENS_DEFAULT
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        if response.ok:
            data = response.json()
            reply = data['choices'][0]['message']['content']
            return jsonify({'response': reply})
        else:
            print('DeepSeek API error:', response.status_code, response.text)
            return jsonify({'response': 'Ocurrió un problema al contactar la API de DeepSeek. Intenta más tarde.'}), 502
    except Exception as e:
        print('Exception al conectar con DeepSeek:', str(e))
        return jsonify({'response': f'Error al contactar la API de DeepSeek: {str(e)}'}), 500

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