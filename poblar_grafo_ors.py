import json
from geopy.distance import geodesic
from app import app
from app.models import Canton

VELOCIDAD_PROMEDIO = 60  # km/h


def poblar_grafo_geodesico(salida_json="grafo_cantonal_geodesico.json"):
    with app.app_context():
        cantones = Canton.query.all()
        nodos = [(c.nombre, c.lat, c.lon) for c in cantones if c.lat is not None and c.lon is not None]
        grafo = {}
        total = len(nodos)
        for i, (nombre_origen, lat1, lon1) in enumerate(nodos):
            grafo[nombre_origen] = {}
            for j, (nombre_destino, lat2, lon2) in enumerate(nodos):
                if nombre_origen == nombre_destino:
                    continue
                distancia_km = geodesic((lat1, lon1), (lat2, lon2)).km
                tiempo_horas = distancia_km / VELOCIDAD_PROMEDIO
                grafo[nombre_origen][nombre_destino] = {
                    'distancia': distancia_km,
                    'tiempo': tiempo_horas * 60,  # en minutos
                    'tipo': 'terrestre'
                }
            print(f"{i+1}/{total} cantones procesados...")
        with open(salida_json, 'w', encoding='utf-8') as f:
            json.dump(grafo, f, ensure_ascii=False, indent=2)
        print(f"Grafo geodésico guardado en {salida_json}")

if __name__ == "__main__":
    poblar_grafo_geodesico()

# poblar_grafo_ors.py
# ---------------------------------------------
# Este script genera un grafo completo entre todos los cantones de Ecuador,
# usando la distancia geodésica (línea recta) entre los centroides de cada cantón.
# Calcula la distancia en kilómetros y estima el tiempo de viaje suponiendo
# una velocidad promedio de 60 km/h. El resultado se guarda en un archivo JSON.
# ---------------------------------------------

import json
from geopy.distance import geodesic
from app import app
from app.models import Canton

VELOCIDAD_PROMEDIO = 60  # km/h


def poblar_grafo_geodesico(salida_json="grafo_cantonal_geodesico.json"):
    """
    Genera un grafo completo entre todos los cantones usando distancia geodésica.
    - Para cada par de cantones, calcula la distancia en línea recta (km)
      y el tiempo estimado suponiendo velocidad promedio.
    - Guarda el resultado en un archivo JSON con la estructura:
      { 'CANTON_ORIGEN': { 'CANTON_DESTINO': {'distancia': km, 'tiempo': min, 'tipo': 'terrestre'}, ... }, ... }
    """
    with app.app_context():
        cantones = Canton.query.all()
        nodos = [(c.nombre, c.lat, c.lon) for c in cantones if c.lat is not None and c.lon is not None]
        grafo = {}
        total = len(nodos)
        for i, (nombre_origen, lat1, lon1) in enumerate(nodos):
            grafo[nombre_origen] = {}
            for j, (nombre_destino, lat2, lon2) in enumerate(nodos):
                if nombre_origen == nombre_destino:
                    continue
                # Calcula distancia geodésica (línea recta) en km
                distancia_km = geodesic((lat1, lon1), (lat2, lon2)).km
                # Tiempo estimado en horas y minutos (asumiendo velocidad promedio)
                tiempo_horas = distancia_km / VELOCIDAD_PROMEDIO
                grafo[nombre_origen][nombre_destino] = {
                    'distancia': distancia_km,
                    'tiempo': tiempo_horas * 60,  # en minutos
                    'tipo': 'terrestre'
                }
            print(f"{i+1}/{total} cantones procesados...")
        # Guarda el grafo completo en archivo JSON
        with open(salida_json, 'w', encoding='utf-8') as f:
            json.dump(grafo, f, ensure_ascii=False, indent=2)
        print(f"Grafo geodésico guardado en {salida_json}")

if __name__ == "__main__":
    poblar_grafo_geodesico()
