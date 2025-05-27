# Este scrip se usa para eliminar un usuario de la base de datos

from app import app, db
from app.models import Usuario

with app.app_context():
    usuario = Usuario.query.filter_by(email='t@gmail.com').first()
    if usuario:
        db.session.delete(usuario)
        db.session.commit()
        print('Usuario eliminado.')
    else:
        print('Usuario no encontrado.')