# =================== Script de Verificación de Base de Datos ===================
#
# Este es un script de utilidad para conectar directamente a la base de datos
# y mostrar el contenido de las tablas principales como 'Usuario' y 'Producto'.
#
# Es muy útil durante el desarrollo para:
# - Verificar que los datos se están guardando correctamente.
# - Depurar problemas relacionados con la información de la base de datos.
# - Realizar comprobaciones rápidas sin necesidad de una herramienta de BD externa.
#
# Para ejecutarlo, simplemente corra `python testingdb.py` desde la raíz del proyecto.
#
# =================== Importaciones ===================
import os
from app import app, db  # Importa la aplicación Flask y la instancia de la base de datos.
from app.models import Usuario, Producto  # Importa los modelos a consultar.

# =================== Configuración de la Base de Datos ===================
# Se asegura de que el script apunte a la base de datos correcta.
# Esta línea es crucial si el script se ejecuta fuera del contexto normal de la app.
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'instance', 'agrogrid.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# =================== Lógica de Consulta ===================
# Se utiliza el contexto de la aplicación para poder interactuar con la base de datos.
with app.app_context():
    print("===========================================")
    print('--- Listado de Usuarios Registrados ---')
    print("===========================================")
    # 1. Consultar todos los usuarios en la tabla 'Usuario'.
    usuarios = Usuario.query.all()
    if not usuarios:
        print("No se encontraron usuarios.")
    else:
        # Iterar sobre los resultados y mostrar la información de cada usuario.
        for u in usuarios:
            print(f"ID: {u.id}, Nombre: {u.name}, Email: {u.email}, Tipo: {u.user_type}, Provincia: {u.provincia}")

    print("\n===========================================")
    print('--- Listado de Productos Registrados ---')
    print("===========================================")
    # 2. Consultar todos los productos, ordenados por ID de forma descendente (los más nuevos primero).
    productos = Producto.query.order_by(Producto.id.desc()).all()
    if not productos:
        print("No se encontraron productos.")
    else:
        # Iterar sobre los resultados y mostrar la información de cada producto.
        for p in productos:
            print(f"ID: {p.id}, Nombre: {p.nombre}, Tipo: {p.tipo}, Región: {p.region}, Provincia: {p.provincia}, Cantón: {p.canton}, Inicial: {p.inicial_nombre}, Precio: {p.precio}, Unidad: {p.unidad}, UsuarioID: {p.usuario_id}, Imagen: {p.imagen_url}") 
    
    # para ejecutar
    # python testingdb.py 