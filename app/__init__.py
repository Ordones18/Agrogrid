# 1. Importaciones de módulos y paquetes necesarios
from flask import Flask  # Framework principal para la aplicación web
from flask_sqlalchemy import SQLAlchemy  # ORM para interactuar con la base de datos
from flask_mail import Mail  # Para el envío de correos electrónicos
import os  # Para interactuar con el sistema operativo (rutas de archivos, variables de entorno)
from dotenv import load_dotenv  # Para cargar variables de entorno desde un archivo .env
from flask_migrate import Migrate  # Para manejar migraciones de la base de datos con Alembic
from flask_login import LoginManager  # Para gestionar las sesiones de usuario (login, logout, etc.)

# 2. Carga de variables de entorno
# Carga las variables definidas en el archivo .env en el entorno de la aplicación.
# Es útil para mantener información sensible (como claves secretas) fuera del código fuente.
load_dotenv()

# 3. Creación e inicialización de la aplicación Flask
app = Flask(__name__)  # Se crea una instancia de la aplicación Flask.
# Se establece una clave secreta para la aplicación, necesaria para la gestión de sesiones y otras características de seguridad.
# Se obtiene del archivo .env para mayor seguridad.
app.secret_key = os.environ.get('SECRET_KEY')

# 4. Configuración de la base de datos SQLAlchemy
# Se define la ruta base del proyecto.
basedir = os.path.abspath(os.path.dirname(__file__))
# Se construye la ruta completa a la base de datos SQLite.
db_path = os.path.join(basedir, '..', 'instance', 'agrogrid.db')
# Se configura la URI de la base de datos para SQLAlchemy.
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
# Se deshabilita el seguimiento de modificaciones de SQLAlchemy para mejorar el rendimiento.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 5. Configuración del servidor de correo (Flask-Mail)
# Se configura el servidor SMTP, puerto y credenciales para el envío de correos.
# Estos valores también se cargan desde el archivo .env.
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')

# 6. Inicialización de extensiones de Flask
db = SQLAlchemy(app)  # Se inicializa SQLAlchemy con la configuración de la app.
mail = Mail(app)  # Se inicializa Flask-Mail.
migrate = Migrate(app, db)  # Se inicializa Flask-Migrate para las migraciones de la base de datos.

# 7. Inicialización de Flask-Login para la gestión de usuarios
login_manager = LoginManager()  # Se crea una instancia de LoginManager.
login_manager.init_app(app)  # Se asocia con la aplicación Flask.
# Se especifica la vista (endpoint) a la que se redirigirá a los usuarios no autenticados
# cuando intenten acceder a una página protegida.
login_manager.login_view = 'login'

# 8. Importación de modelos y definición del cargador de usuario
# Se importa el modelo de usuario para que Flask-Login pueda trabajar con él.
from app.models import Usuario

# Esta función es un "decorador" de Flask-Login que se utiliza para recargar el objeto de usuario
# desde el ID de usuario almacenado en la sesión.
@login_manager.user_loader
def load_user(user_id):
    # Devuelve el usuario correspondiente al ID proporcionado.
    return Usuario.query.get(int(user_id))

# 9. Importación de las rutas (vistas) de la aplicación
# Se importa el módulo de rutas al final para evitar importaciones circulares,
# ya que el módulo de rutas necesita importar la variable 'app' definida en este archivo.
from app import routes