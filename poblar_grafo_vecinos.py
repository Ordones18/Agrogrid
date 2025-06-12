import geopandas as gpd
import json
from geopy.distance import geodesic

# Ruta al geojson de cantones descargado del repositorio
CANTONES_GEOJSON = "geojson/cantons.geojson"
SALIDA_GRAFO = "grafo_cantonal_vecinos.json"
VELOCIDAD_PROMEDIO = 60  # km/h

import unicodedata

def normaliza(nombre):
    return unicodedata.normalize('NFKD', nombre).encode('ASCII', 'ignore').decode('ASCII').strip().upper()

def obtener_vecinos_por_canton(gdf):
    """
    Devuelve un diccionario {canton: [vecinos]} usando el método de intersección de polígonos.
    Todos los nombres son normalizados.
    """
    vecinos = {normaliza(row['canton']): set() for _, row in gdf.iterrows()}
    for idx, canton in gdf.iterrows():
        canton_geom = canton.geometry
        nombre = normaliza(canton['canton'])
        for idx2, vecino in gdf.iterrows():
            vecino_nombre = normaliza(vecino['canton'])
            if nombre == vecino_nombre:
                continue
            # Usar buffer pequeño y .intersects() para mejorar la detección de vecinos
            if canton_geom.buffer(0.001).intersects(vecino.geometry.buffer(0.001)):
                vecinos[nombre].add(vecino_nombre)
    # Convertir sets a listas
    return {k: list(v) for k, v in vecinos.items()}


def poblar_grafo_vecinos():
    gdf = gpd.read_file(CANTONES_GEOJSON)
    vecinos = obtener_vecinos_por_canton(gdf)
    
    # Obtener centroide de cada cantón para las distancias
    centroides = {normaliza(row['canton']): (row.geometry.centroid.y, row.geometry.centroid.x) for _, row in gdf.iterrows()}
    
    grafo = {}
    for origen, lista_vecinos in vecinos.items():
        grafo[origen] = {}
        for destino in lista_vecinos:
            latlon1 = centroides[origen]
            latlon2 = centroides[destino]
            distancia_km = geodesic(latlon1, latlon2).km
            tiempo_horas = distancia_km / VELOCIDAD_PROMEDIO
            grafo[origen][destino] = {
                'distancia': distancia_km,
                'tiempo': tiempo_horas * 60,
                'tipo': 'terrestre'
            }
    # --- AGREGAR RUTAS MARÍTIMAS DESDE CUALQUIER CANTÓN HACIA GALÁPAGOS ---
    GALAPAGOS = ['SAN CRISTOBAL', 'ISABELA', 'SANTA CRUZ']
    DISTANCIA_MARITIMA = 1200  # km fijo
    TIEMPO_MARITIMO = DISTANCIA_MARITIMA / VELOCIDAD_PROMEDIO * 60
    todos_cantones = list(grafo.keys())
    for isla in GALAPAGOS:
        for canton in todos_cantones:
            if canton not in GALAPAGOS:
                # ida
                grafo.setdefault(canton, {})[isla] = {
                    'distancia': DISTANCIA_MARITIMA,
                    'tiempo': TIEMPO_MARITIMO,
                    'tipo': 'maritimo'
                }
                # vuelta
                grafo.setdefault(isla, {})[canton] = {
                    'distancia': DISTANCIA_MARITIMA,
                    'tiempo': TIEMPO_MARITIMO,
                    'tipo': 'maritimo'
                }
    with open(SALIDA_GRAFO, 'w', encoding='utf-8') as f:
        json.dump(grafo, f, ensure_ascii=False, indent=2)
    print(f"Grafo de vecinos guardado en {SALIDA_GRAFO}")

if __name__ == "__main__":
    poblar_grafo_vecinos()
