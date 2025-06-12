# ver_cantones_latlon.py
# Script para visualizar todos los cantones y sus coordenadas desde la base de datos

from app import app
from app.models import Canton

with app.app_context():
    cantones = Canton.query.order_by(Canton.nombre).all()
    print(f"{'ID':<5} {'Nombre':<30} {'Latitud':<15} {'Longitud':<15}")
    print("-" * 70)
    for canton in cantones:
        lat = canton.lat if canton.lat is not None else ''
        lon = canton.lon if canton.lon is not None else ''
        print(f"{canton.id:<5} {canton.nombre:<30} {lat:<15} {lon:<15}")
    print("\nResumen:")
    con_coords = sum(1 for c in cantones if c.lat is not None and c.lon is not None)
    sin_coords = len(cantones) - con_coords
    print(f"Cantones CON coordenadas: {con_coords}")
    print(f"Cantones SIN coordenadas: {sin_coords}")
