# test_db.py
# Este scrip se utiliza para visualizar los usuarios en la base de datos
from app import app, db
from app.models import Usuario

with app.app_context():
    usuarios = Usuario.query.all()
    for usuario in usuarios:
        print(f'ID: {usuario.id}, Email: {usuario.email}, Nombre: {usuario.name}, Tipo: {usuario.user_type}')

