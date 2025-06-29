# =================== Importaciones principales ===================

from werkzeug.security import generate_password_hash  # Para hashear contraseñas de usuarios
from app import db  # Instancia de SQLAlchemy para la base de datos
from datetime import datetime

# Tabla de asociación para favoritos (Usuario <-> Producto)
favoritos = db.Table('favoritos',
    db.Column('usuario_id', db.Integer, db.ForeignKey('usuario.id'), primary_key=True),
    db.Column('producto_id', db.Integer, db.ForeignKey('producto.id'), primary_key=True)
)

# =========================
# Modelo de Usuario
# =========================
class Usuario(db.Model):
    """
    Modelo que representa a un usuario del sistema AgroGrid.
    Puede ser agricultor, comprador o transportista.
    """
    id = db.Column(db.Integer, primary_key=True) # Identificador único del usuario (clave primaria)
    name = db.Column(db.String(100), nullable=False) # Nombre completo del usuario
    email = db.Column(db.String(120), unique=True, nullable=False) # Correo electrónico único del usuario
    user_type = db.Column(db.String(50), nullable=False) # Tipo de usuario (agricultor, comprador, transportista)
    provincia = db.Column(db.String(50), nullable=False) # Provincia de residencia del usuario
    cedula = db.Column(db.String(20)) # Cédula de identidad del usuario (opcional)
    phone = db.Column(db.String(20), nullable=False) # Número de teléfono del usuario
    password = db.Column(db.String(128), nullable=False) # Contraseña hasheada del usuario

    # Relación de favoritos: productos marcados como favoritos por el usuario
    favoritos = db.relationship(
        'Producto',
        secondary='favoritos',
        backref=db.backref('usuarios_favoritos', lazy='dynamic'),
        lazy='dynamic'
    )

    def set_password(self, password):
        """
        Hashea y establece la contraseña del usuario.
        Args:
            password (str): Contraseña en texto plano
        """
        self.password = generate_password_hash(password)

    # Métodos requeridos por Flask-Login
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)


# =========================
# Modelos de Ubicación Jerárquica
# =========================
class Region(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    provincias = db.relationship('Provincia', backref='region', lazy=True)

class Provincia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'), nullable=False)
    cantones = db.relationship('Canton', backref='provincia', lazy=True)

class Canton(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    provincia_id = db.Column(db.Integer, db.ForeignKey('provincia.id'), nullable=False)
    lat = db.Column(db.Float, nullable=True)  # Latitud
    lon = db.Column(db.Float, nullable=True)  # Longitud

# =========================
# Modelos de Taxonomía de Productos
# =========================
class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    subcategorias = db.relationship('Subcategoria', backref='categoria', lazy=True)

class Subcategoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('subcategoria.id'), nullable=True)  # Para subcategoría anidada
    hijos = db.relationship('Subcategoria', backref=db.backref('padre', remote_side=[id]), lazy=True)
    # El backref 'subcategoria' se define en Producto

# =========================
# Modelo de Producto
# =========================
class Producto(db.Model):
    __tablename__ = 'producto'
    id = db.Column(db.Integer, primary_key=True)  # Identificador único del producto (clave primaria)
    nombre = db.Column(db.String(100), nullable=False)  # Nombre del producto
    tipo = db.Column(db.String(50), nullable=False)  # Tipo de producto (Fruta, Verdura, etc.)
    region = db.Column(db.String(30), nullable=False)  # Región ecuatoriana de origen
    provincia = db.Column(db.String(50), nullable=False)  # Provincia de origen
    inicial_nombre = db.Column(db.String(1), nullable=False)  # Inicial del nombre del producto (para grafos o agrupaciones)
    imagen_url = db.Column(db.String(200))  # Ruta de la imagen subida (opcional)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)  # ID del usuario agricultor que publica el producto
    precio = db.Column(db.Float, nullable=True)  # Precio del producto
    unidad = db.Column(db.String(20), nullable=True)  # Unidad de medida (Kg, Quintal, etc.)
    descripcion = db.Column(db.Text, nullable=True)  # Descripción detallada del producto
    cantidad = db.Column(db.Float, nullable=True)  # Cantidad disponible del producto
    vistas = db.Column(db.Integer, default=0)  # Número de vistas del producto
    subcategoria_id = db.Column(db.Integer, db.ForeignKey('subcategoria.id'), nullable=False)  # Relación obligatoria con subcategoría
    usuario = db.relationship('Usuario', backref=db.backref('productos', lazy=True))
    canton = db.Column(db.String(50), nullable=True)  # Campo para cantón agregado (opcional)


# =========================
# Modelo de Carrito de Compras
# =========================
class Carrito(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comprador_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    detalles = db.relationship('DetalleCarrito', backref='carrito', lazy=True)
    estado = db.Column(db.String(20), default='activo')  # activo, comprado, cancelado

class DetalleCarrito(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    carrito_id = db.Column(db.Integer, db.ForeignKey('carrito.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    cantidad = db.Column(db.Float, nullable=False)
    producto = db.relationship('Producto')

# =========================
# Modelo de Testimonio
# =========================
class Testimonio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo_usuario = db.Column(db.String(50), nullable=False)  # Agricultor, Comprador, Transportista, etc.
    mensaje = db.Column(db.Text, nullable=False)
    avatar_url = db.Column(db.String(200), nullable=True)  # Opcional: URL de imagen/avatar
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Testimonio {self.nombre} - {self.tipo_usuario}>'

# =========================
# Modelos de Orden y OrdenItem
# =========================
class Orden(db.Model):
    """
    Representa un pedido de compra realizado por un usuario.
    Contiene el total, el estado y los productos asociados a través de OrdenItem.
    """
    id = db.Column(db.Integer, primary_key=True)  # ID único de la orden.
    comprador_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)  # ID del usuario que realizó la compra.
    total = db.Column(db.Float, nullable=False)  # Costo total de los productos en la orden.
    costo_envio = db.Column(db.Float, nullable=True, default=0)  # Costo del envío, calculado por el transportista.
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)  # Fecha y hora de creación de la orden.
    estado = db.Column(db.String(20), default='pendiente')  # Estado actual de la orden (e.g., pendiente, pagada, enviada).
    calificacion = db.Column(db.Integer, nullable=True)  # Calificación de la orden (1-5) dada por el comprador.
    items = db.relationship('OrdenItem', backref='orden', cascade='all, delete-orphan')  # Relación con los artículos de la orden.
    viaje = db.relationship('Viaje', backref='orden', uselist=False)  # Relación uno-a-uno con el viaje de transporte.

# =========================
# Modelo de Vehículo
# =========================
class Vehiculo(db.Model):
    """
    Representa un vehículo perteneciente a un transportista.
    Almacena detalles como placa, tipo y capacidad para la logística.
    """
    id = db.Column(db.Integer, primary_key=True)  # ID único del vehículo.
    transportista_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)  # ID del transportista propietario.
    placa = db.Column(db.String(20), nullable=False, unique=True)  # Placa única del vehículo.
    tipo = db.Column(db.String(50), nullable=False)  # Tipo de vehículo (e.g., Camión, Furgoneta).
    capacidad = db.Column(db.String(50), nullable=True)  # Capacidad de carga (e.g., '3.5 Toneladas').
    descripcion = db.Column(db.Text, nullable=True)  # Descripción adicional del vehículo.
    imagen_url = db.Column(db.String(200), nullable=True)  # URL de una imagen del vehículo.
    transportista = db.relationship('Usuario', backref=db.backref('vehiculos', lazy=True)) # Relación con el usuario transportista.

# =========================
# Modelo de Viaje
# =========================
class Viaje(db.Model):
    """
    Representa el componente logístico de una orden.
    Asocia una orden con un transportista y rastrea el estado de la entrega.
    """
    id = db.Column(db.Integer, primary_key=True)  # ID único del viaje.
    orden_id = db.Column(db.Integer, db.ForeignKey('orden.id'), nullable=False, unique=True)  # ID de la orden asociada (relación uno-a-uno).
    transportista_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True)  # ID del transportista asignado.
    estado = db.Column(db.String(20), default='pendiente')  # Estado del viaje (e.g., pendiente, en_progreso, entregado).
    fecha_asignacion = db.Column(db.DateTime, nullable=True)  # Fecha en que el transportista acepta el viaje.
    fecha_entrega = db.Column(db.DateTime, nullable=True)  # Fecha en que se completa la entrega.
    origen = db.Column(db.String(200), nullable=True)  # Dirección de origen (del agricultor).
    destino = db.Column(db.String(200), nullable=True)  # Dirección de destino (del comprador).
    costo = db.Column(db.Float, nullable=True)  # Costo del transporte acordado.
    notas = db.Column(db.Text, nullable=True)  # Notas adicionales del transportista o comprador.
    calificacion = db.Column(db.Integer, nullable=True)  # Calificación del servicio de transporte (1-5).
    transportista = db.relationship('Usuario', foreign_keys=[transportista_id])  # Relación con el usuario transportista.

class OrdenItem(db.Model):
    """
    Representa un único artículo dentro de una orden de compra.
    Almacena una 'snapshot' (copia) de los detalles del producto en el momento de la compra
    para mantener la integridad del historial de pedidos.
    """
    id = db.Column(db.Integer, primary_key=True)  # ID único del ítem de la orden.
    orden_id = db.Column(db.Integer, db.ForeignKey('orden.id'), nullable=False)  # ID de la orden a la que pertenece.
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)  # ID del producto original.
    cantidad = db.Column(db.Integer, nullable=False)  # Cantidad comprada del producto.
    precio_unitario = db.Column(db.Float, nullable=False)  # Precio del producto en el momento de la compra.
    # --- Snapshots de datos del producto ---
    producto_nombre = db.Column(db.String(100), nullable=True)  # Nombre del producto al momento de la compra.
    producto_unidad = db.Column(db.String(20), nullable=True)  # Unidad de medida al momento de la compra.
    producto = db.relationship('Producto')  # Relación con el producto original para fácil acceso.

