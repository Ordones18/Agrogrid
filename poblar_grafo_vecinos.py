# =================== Script para Generar Grafo de Vecinos ===================
#
# Este script construye un grafo de transporte basado en la adyacencia geográfica
# (vecindad) de los cantones de Ecuador, utilizando un archivo GeoJSON.
#
# Funcionamiento:
# 1. Lee un archivo GeoJSON que contiene los polígonos de cada cantón.
# 2. Identifica qué cantones son vecinos directos al comprobar si sus polígonos se tocan.
# 3. Para cada par de vecinos, calcula la distancia geodésica entre sus centroides.
# 4. Estima el tiempo de viaje basado en una velocidad promedio.
# 5. Agrega conexiones marítimas especiales entre todos los cantones continentales
#    y los cantones de Galápagos, con una distancia y tiempo fijos.
# 6. Guarda el grafo resultante en un archivo JSON.
#
# Dependencias: geopandas, geopy, y un archivo GeoJSON con los polígonos cantonales.
#
# =================== Importaciones ===================
import geopandas as gpd  # Para leer y manipular datos geoespaciales (archivos GeoJSON).
import json              # Para guardar el grafo resultante en formato JSON.
from geopy.distance import geodesic  # Para calcular distancias entre coordenadas.
import unicodedata       # Para la normalización de texto (eliminar tildes).

# =================== Constantes y Configuración ===================
# Ruta al archivo GeoJSON que contiene los polígonos de los cantones.
CANTONES_GEOJSON = "geojson/cantons.geojson"
# Nombre del archivo de salida para el grafo generado.
SALIDA_GRAFO = "grafo_cantonal_vecinos.json"
# Velocidad promedio en km/h para estimar tiempos de viaje.
VELOCIDAD_PROMEDIO = 60


def normaliza(nombre):
    """Normaliza un nombre de cantón: sin tildes, sin espacios extra y en mayúsculas."""
    return unicodedata.normalize('NFKD', nombre).encode('ASCII', 'ignore').decode('ASCII').strip().upper()

def obtener_vecinos_por_canton(gdf):
    """
    Analiza un GeoDataFrame y devuelve un diccionario de vecinos para cada cantón.

    La vecindad se determina si los polígonos de dos cantones se intersectan.
    Se usa un pequeño buffer para asegurar la detección de fronteras que solo se tocan.

    Args:
        gdf (GeoDataFrame): GeoDataFrame de GeoPandas con la geometría de los cantones.

    Returns:
        dict: Un diccionario donde cada clave es un cantón normalizado y el valor es una
              lista de sus cantones vecinos normalizados.
    """
    print("Identificando vecinos por intersección de polígonos...")
    vecinos = {normaliza(row['canton']): set() for _, row in gdf.iterrows()}
    for idx, canton in gdf.iterrows():
        canton_geom = canton.geometry
        nombre = normaliza(canton['canton'])
        # Compara cada cantón con todos los demás para encontrar vecinos.
        for idx2, vecino in gdf.iterrows():
            vecino_nombre = normaliza(vecino['canton'])
            if nombre == vecino_nombre:
                continue
            # Se usa un buffer(0.001) para evitar falsos negativos en polígonos que solo se tocan.
            if canton_geom.buffer(0.001).intersects(vecino.geometry.buffer(0.001)):
                vecinos[nombre].add(vecino_nombre)
    print("Identificación de vecinos completada.")
    # Convertir los sets de vecinos a listas para el formato final.
    return {k: list(v) for k, v in vecinos.items()}


def poblar_grafo_vecinos():
    """
    Función principal que orquesta la creación del grafo de vecinos.
    """
    print(f"Cargando datos geoespaciales desde '{CANTONES_GEOJSON}'...")
    gdf = gpd.read_file(CANTONES_GEOJSON)
    
    # 1. Obtener la lista de adyacencia de los cantones.
    vecinos = obtener_vecinos_por_canton(gdf)
    
    # 2. Calcular el centroide (punto central) de cada cantón para medir distancias.
    print("Calculando centroides de los cantones...")
    centroides = {normaliza(row['canton']): (row.geometry.centroid.y, row.geometry.centroid.x) for _, row in gdf.iterrows()}
    
    # 3. Construir el grafo terrestre basado en la vecindad.
    print("Construyendo grafo de rutas terrestres entre vecinos...")
    grafo = {}
    for origen, lista_vecinos in vecinos.items():
        grafo[origen] = {}
        for destino in lista_vecinos:
            latlon1 = centroides[origen]
            latlon2 = centroides[destino]
            # Calcular distancia y tiempo entre los centroides de los cantones vecinos.
            distancia_km = geodesic(latlon1, latlon2).km
            tiempo_horas = distancia_km / VELOCIDAD_PROMEDIO
            grafo[origen][destino] = {
                'distancia': round(distancia_km, 2),
                'tiempo': round(tiempo_horas * 60, 2), # en minutos
                'tipo': 'terrestre'
            }

    # 4. Agregar rutas marítimas desde CUALQUIER cantón continental hacia Galápagos.
    print("Agregando rutas marítimas hacia Galápagos...")
    GALAPAGOS = ['SAN CRISTOBAL', 'ISABELA', 'SANTA CRUZ']
    DISTANCIA_MARITIMA = 1200  # Distancia fija estimada en km.
    TIEMPO_MARITIMO = DISTANCIA_MARITIMA / VELOCIDAD_PROMEDIO * 60 # en minutos
    
    todos_cantones_continentales = [c for c in grafo.keys() if c not in GALAPAGOS]

    for isla in GALAPAGOS:
        for canton_continental in todos_cantones_continentales:
            # Crear conexión de ida (continente -> isla).
            grafo.setdefault(canton_continental, {})[isla] = {
                'distancia': DISTANCIA_MARITIMA,
                'tiempo': TIEMPO_MARITIMO,
                'tipo': 'maritimo'
            }
            # Crear conexión de vuelta (isla -> continente).
            grafo.setdefault(isla, {})[canton_continental] = {
                'distancia': DISTANCIA_MARITIMA,
                'tiempo': TIEMPO_MARITIMO,
                'tipo': 'maritimo'
            }
            
    # 5. Guardar el grafo final en un archivo JSON.
    with open(SALIDA_GRAFO, 'w', encoding='utf-8') as f:
        json.dump(grafo, f, ensure_ascii=False, indent=2)
    print(f"\n¡Éxito! Grafo de vecinos con rutas marítimas guardado en '{SALIDA_GRAFO}'")


if __name__ == "__main__":
    print("======================================================")
    print("Iniciando la generación del grafo de vecinos...")
    print("======================================================")
    poblar_grafo_vecinos()
    print("======================================================")
    print("Proceso de generación de grafo finalizado.")
    print("======================================================")
