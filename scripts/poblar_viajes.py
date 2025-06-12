# Script para poblar la tabla Viaje a partir de órdenes existentes
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, db
from app.models import Orden, Viaje

with app.app_context():
    ordenes = Orden.query.all()
    creados = 0
    for orden in ordenes:
        # Si la orden ya tiene un viaje, saltar
        if hasattr(orden, 'viaje') and orden.viaje:
            continue
        # Crear viaje pendiente para cada orden
        # Obtener primer producto y su agricultor
        primer_item = orden.items[0] if orden.items else None
        producto = primer_item.producto if primer_item else None
        agricultor = producto.usuario if producto else None
        origen = None
        if producto and agricultor:
            canton = producto.canton or ''
            provincia = producto.provincia or ''
            nombre_agricultor = agricultor.name or ''
            origen = f"{canton}, {provincia} — Agricultor: {nombre_agricultor}"
        else:
            origen = 'Sin datos de agricultor'

        # Obtener comprador
        comprador = orden.comprador_id
        comprador_usuario = None
        if comprador:
            from app.models import Usuario
            comprador_usuario = Usuario.query.get(comprador)
        destino = None
        if comprador_usuario:
            provincia = comprador_usuario.provincia or ''
            nombre_comprador = comprador_usuario.name or ''
            destino = f"{provincia} — Comprador: {nombre_comprador}"
        else:
            destino = 'Sin datos de comprador'

        viaje = Viaje(
            orden_id=orden.id,
            estado='pendiente',
            origen=origen,
            destino=destino,
        )
        db.session.add(viaje)
        creados += 1
    db.session.commit()
    print(f"Viajes creados: {creados}")
