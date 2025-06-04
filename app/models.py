# =================== Importaciones principales ===================

from werkzeug.security import generate_password_hash  # Para hashear contraseñas de usuarios
from app import db  # Instancia de SQLAlchemy para la base de datos
from datetime import datetime

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
# Modelos de Orden y OrdenItem
# =========================
class Orden(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comprador_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    total = db.Column(db.Float, nullable=False)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(20), default='pendiente')
    items = db.relationship('OrdenItem', backref='orden', cascade='all, delete-orphan')

class OrdenItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    orden_id = db.Column(db.Integer, db.ForeignKey('orden.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    producto = db.relationship('Producto')

