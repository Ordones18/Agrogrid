# =================== Importaciones principales ===================

from flask import render_template, request, redirect, url_for, flash, session, send_file, jsonify  # Funciones principales de Flask para manejo de vistas, formularios, sesiones y respuestas
from app import app, mail, db  # Instancias principales de la app, correo y base de datos
from flask_mail import Message  # Para enviar correos electrónicos
from app.models import Usuario, Producto  # Modelos de la base de datos
from werkzeug.security import generate_password_hash, check_password_hash  # Utilidades para hashear y verificar contraseñas
from .utils import generate_token, confirm_token  # Funciones utilitarias para manejo de tokens (recuperación de contraseña, etc.)
from werkzeug.utils import secure_filename  # Para guardar archivos de forma segura
import os  # Manejo de rutas y sistema operativo
from flask import current_app  # Acceso a la app actual de Flask
import io  # Manejo de streams de datos (para imágenes, gráficos)
import numpy as np  # Librería para cálculos numéricos y arreglos (usada en analítica)
import matplotlib.pyplot as plt  # Librería para generación de gráficos estáticos


# =================== Rutas Públicas ===================

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

@app.route('/logout')
def logout():
    """
    Cierra la sesión del usuario.
    - Método: GET
    - Request: Ninguno
    - Response: Redirige a login
    """
    session.pop('user', None)
    session.pop('user_type', None)
    flash('Has cerrado sesión exitosamente.', 'success')
    return redirect(url_for('login'))

# =================== Perfiles de Usuario ===================

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
    ventas_totales_calculadas = 0.00
    numero_productos_publicados = len(productos_del_agricultor)
    vistas_a_productos = 0

    return render_template('agricultor/perfil_agricultor.html',
                           user=usuario,
                           productos=productos_del_agricultor,
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
    # Asegúrate de que el usuario exista y maneja el caso contrario
    if not usuario:
        flash('Usuario no encontrado.', 'danger')
        session.pop('user', None)
        session.pop('user_type', None)
        return redirect(url_for('login'))

    return render_template('comprador/perfil_comprador.html',  
                           user=usuario,
                           user_type=session['user_type'])

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

# =================== Gestión de Productos ===================

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

    # Crea el producto y lo guarda en la base de datos
    producto = Producto(
        nombre=nombre,
        tipo=tipo,
        region=region,
        provincia=provincia,
        inicial_nombre=inicial_nombre,
        imagen_url=imagen_url,
        usuario_id=usuario.id,
        precio=precio,
        unidad=unidad,
        descripcion=descripcion,
        cantidad=cantidad
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

# =================== Analítica y APIs ===================

@app.route('/grafico/vistas_productos')
def grafico_vistas_productos():
    """
    Devuelve un gráfico PNG de vistas por producto (versión estática).
    - Método: GET
    - Requiere autenticación como agricultor.
    - Response: Imagen PNG
    """
    if 'user' not in session or session.get('user_type') != 'agricultor':
        return '', 403

    usuario = Usuario.query.filter_by(email=session['user']).first()
    productos = Producto.query.filter_by(usuario_id=usuario.id).all()
    nombres = [p.nombre for p in productos]
    vistas = [p.vistas or 0 for p in productos]

    # Si no hay productos, muestra un gráfico vacío
    if not nombres:
        nombres = ['Sin productos']
        vistas = [0]

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(nombres, vistas, color='green')
    ax.set_ylabel('Vistas')
    ax.set_title('Vistas por Producto')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)
    return send_file(buf, mimetype='image/png')

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

# =================== Utilidades y Context Processors ===================

@app.context_processor
def inject_user():
    """
    Inyecta el usuario y tipo de usuario en el contexto de las plantillas.
    """
    return {
        'user': session.get('user'),
        'user_type': session.get('user_type')
    }

