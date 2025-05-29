from flask import render_template, request, redirect, url_for, flash, session
from app import app, mail, db
from flask_mail import Message
from app.models import Usuario, Producto
from werkzeug.security import generate_password_hash, check_password_hash
from .utils import generate_token, confirm_token
from werkzeug.utils import secure_filename
import os
from flask import current_app


# Ruta para la página de inicio
@app.route('/')
def index():
    user = session.get('user')
    user_type = session.get('user_type')
    return render_template('index.html', user=user, user_type=user_type)

@app.route('/about')
def about():
    return render_template('about.html')




# Ruta para la página de explorar
@app.route('/explore')
def explore():
    return render_template('explore.html')

# Ruta para la página de inicio de sesión
@app.route('/register', methods=['GET', 'POST'])
def register():
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

# Ruta para la página de inicio de sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
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

# Ruta para la página de perfil del agricultor
@app.route('/perfil/agricultor')
def perfil_agricultor():
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

# Ruta para agregar un producto
@app.route('/producto/agregar', methods=['POST'])
def agregar_producto():
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
        unidad=unidad
    )
    db.session.add(producto)
    db.session.commit()

    flash('Producto agregado correctamente.', 'success')
    return redirect(url_for('perfil_agricultor'))

# Ruta del perfil de comprador
# Ruta del perfil de comprador
@app.route('/perfil/comprador')
def perfil_comprador():
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

    return render_template('comprador/perfil_comprador.html',  # Asegúrate que esta línea sea la correcta
                           user=usuario,
                           user_type=session['user_type'])

# Ruta del perfil de transportista
@app.route('/perfil/transportista')
def perfil_transportista():
    if 'user' not in session:
        return redirect(url_for('login'))
    if session.get('user_type') != 'transportista':
        flash('No tienes permiso para acceder a esta página', 'danger')
        return redirect(url_for('login'))

    usuario = Usuario.query.filter_by(email=session['user']).first()
    return render_template('transportista/perfil_transportista.html',
                           user=usuario,
                           user_type=session['user_type'])

# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('user_type', None)
    flash('Has cerrado sesión exitosamente.', 'success')
    return redirect(url_for('login'))

@app.context_processor
def inject_user():
    return {
        'user': session.get('user'),
        'user_type': session.get('user_type')
    }

@app.route('/producto/editar/<int:producto_id>', methods=['GET', 'POST'])
def editar_producto(producto_id):
    # Lógica para editar el producto
    return "Funcionalidad de edición próximamente"

@app.route('/producto/eliminar/<int:producto_id>', methods=['POST', 'GET'])
def eliminar_producto(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    # Opcional: verifica que el usuario sea el dueño del producto
    db.session.delete(producto)
    db.session.commit()
    flash('Producto eliminado correctamente.', 'success')
    return redirect(url_for('perfil_agricultor'))