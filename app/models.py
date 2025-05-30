# =================== Importaciones principales ===================

from werkzeug.security import generate_password_hash  # Para hashear contraseñas de usuarios
from app import db  # Instancia de SQLAlchemy para la base de datos

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

# =========================
# Modelo de Producto
# =========================
class Producto(db.Model):
    """
    Modelo que representa un producto agrícola publicado por un agricultor.
    Incluye información relevante para la gestión y visualización en AgroGrid.
    """
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

    # Relación con el usuario (agricultor)
    usuario = db.relationship('Usuario', backref=db.backref('productos', lazy=True))
