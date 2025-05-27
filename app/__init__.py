from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
import os # Para manejar rutas y variables de entorno
from dotenv import load_dotenv
# Carga las variables de entorno desde el archivo .env
load_dotenv()

app = Flask(__name__) # Crea la instancia de Flask
app.secret_key = os.environ.get('SECRET_KEY') # Carga la clave secreta desde las variables de entorno

# Asegura la ruta absoluta para la base de datos
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, '..', 'instance', 'agrogrid.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuración de correo
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')

db = SQLAlchemy(app) # Crea la instancia de SQLAlchemy
mail = Mail(app) # Crea la instancia de Mail


from app import routes