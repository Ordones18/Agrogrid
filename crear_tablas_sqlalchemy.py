# crear_tablas_sqlalchemy.py
# Script para crear todas las tablas gestionadas por SQLAlchemy (incluyendo Usuario) en la base de datos actual.
# Ejecuta este script una sola vez después de borrar la base de datos o al iniciar el proyecto desde cero.

from app import db, app

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("¡Tablas SQLAlchemy creadas exitosamente!")

# Parámetros esperados para registro de usuario:
# name, email, user_type, provincia, cedula, phone, password
# Ejemplo de registro (POST):
# {
#     "name": "Juan Perez",
#     "email": "juan@mail.com",
#     "user_type": "agricultor",
#     "provincia": "Napo",
#     "cedula": "1234567890",
#     "phone": "0999999999",
#     "password": "tu_clave"
# }
