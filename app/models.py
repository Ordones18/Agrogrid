from werkzeug.security import generate_password_hash
from app import db # Importa la instancia de SQLAlchemy (db) desde tu aplicación Flask

class Usuario(db.Model): # Define una clase llamada Usuario que hereda de db.Model, lo que la convierte en un modelo de SQLAlchemy
    id = db.Column(db.Integer, primary_key=True) # Define una columna 'id' de tipo Integer, que es la clave primaria de la tabla
    name = db.Column(db.String(100), nullable=False) # Define una columna 'name' de tipo String con un máximo de 100 caracteres, no puede ser nula
    email = db.Column(db.String(120), unique=True, nullable=False) # Define una columna 'email' de tipo String con un máximo de 120 caracteres, debe ser única y no puede ser nula
    user_type = db.Column(db.String(50), nullable=False) # Define una columna 'user_type' de tipo String con un máximo de 50 caracteres, no puede ser nula (ej. 'agricultor', 'comprador')
    provincia = db.Column(db.String(50), nullable=False) # Define una columna 'provincia' de tipo String con un máximo de 50 caracteres, no puede ser nula
    cedula = db.Column(db.String(20)) # Define una columna 'cedula' de tipo String con un máximo de 20 caracteres, puede ser nula
    phone = db.Column(db.String(20), nullable=False) # Define una columna 'phone' de tipo String con un máximo de 20 caracteres, no puede ser nula
    password = db.Column(db.String(128), nullable=False) # Define una columna 'password' de tipo String con un máximo de 128 caracteres (para almacenar el hash de la contraseña), no puede ser nula

    def set_password(self, password):
        self.password = generate_password_hash(password)