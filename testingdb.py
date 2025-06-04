import os
from app import app, db
from app.models import Usuario, Producto

# Configura la base de datos de testing
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/agrogrid.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

with app.app_context():
    print('--- Usuarios registrados ---')
    usuarios = Usuario.query.all()
    for u in usuarios:
        print(f"ID: {u.id}, Nombre: {u.name}, Email: {u.email}, Tipo: {u.user_type}, Provincia: {u.provincia}")

    print('\n--- Productos registrados ---')
    productos = Producto.query.order_by(Producto.id.desc()).all()
    for p in productos:
        print(f"ID: {p.id}, Nombre: {p.nombre}, Tipo: {p.tipo}, Región: {p.region}, Provincia: {p.provincia}, Inicial: {p.inicial_nombre}, Precio: {p.precio}, Unidad: {p.unidad}, UsuarioID: {p.usuario_id}, Imagen: {p.imagen_url}") 
    
    # para ejecutar
    # python testingdb.py 