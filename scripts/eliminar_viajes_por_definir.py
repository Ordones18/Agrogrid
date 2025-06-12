# Script para eliminar viajes con origen o destino 'Por definir'
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, db
from app.models import Viaje

with app.app_context():
    eliminados = Viaje.query.filter(
        (Viaje.origen == 'Por definir') | (Viaje.destino == 'Por definir')
    ).delete(synchronize_session=False)
    db.session.commit()
    print(f"Viajes eliminados: {eliminados}")
