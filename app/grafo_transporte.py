# Importaciones necesarias
from heapq import heappush, heappop  # Para implementar la cola de prioridad (min-heap) en Dijkstra.
from typing import Dict, Tuple, List  # Para el tipado estático, mejorando la legibilidad.
import os  # Para interactuar con el sistema de archivos (rutas).
import json  # Para leer y escribir datos en formato JSON.
from app.models import Canton  # Modelo de la base de datos para acceder a los cantones.
from app import app  # Importa la instancia de la aplicación Flask para obtener el contexto de la app.

# Inicialización del grafo cantonal
# Este diccionario almacenará el grafo de transporte que se usará en toda la aplicación.
grafo_cantonal = {}


# La estructura del grafo es un diccionario de diccionarios:
# {canton_origen: {canton_destino: {'distancia': km, 'tipo': 'terrestre'/'maritimo'}}}
def generar_grafo_completo_cantones(distancia_fija=100, tipo='terrestre'):
    """
    Genera un grafo completo donde todos los cantones están conectados entre sí.
    Útil para pruebas o como una configuración inicial si no hay datos de vecinos reales.
    """
    grafo = {}
    # Se necesita el contexto de la aplicación para realizar consultas a la base de datos.
    with app.app_context():
        cantones = [c.nombre for c in Canton.query.all()]
        for origen in cantones:
            grafo[origen] = {}
            for destino in cantones:
                if origen != destino:
                    grafo[origen][destino] = {'distancia': distancia_fija, 'tipo': tipo}
    return grafo

# Carga del grafo desde un archivo JSON
# Este bloque de código se ejecuta una sola vez cuando el módulo es importado.
# Intenta cargar las conexiones del grafo desde un archivo pre-generado.

# Construye la ruta absoluta al archivo JSON que contiene el grafo.
GRAFO_JSON_PATH = os.path.join(os.path.dirname(__file__), '..', 'grafo_cantonal_vecinos.json')
try:
    # Intenta abrir y cargar el archivo JSON.
    with open(GRAFO_JSON_PATH, 'r', encoding='utf-8') as f:
        grafo_cantonal = json.load(f)
    print(f"[INFO] Grafo cantonal cargado exitosamente desde {GRAFO_JSON_PATH}")
except FileNotFoundError:
    # Si el archivo no existe, se imprime una advertencia y el grafo queda vacío.
    print(f"[ADVERTENCIA] No se encontró {GRAFO_JSON_PATH}. El grafo cantonal está vacío.")
    grafo_cantonal = {}

# Implementación del Algoritmo de Dijkstra
def dijkstra(grafo: Dict[str, Dict[str, Dict]], origen: str, destino: str) -> Tuple[float, List[str], List[str]]:
    """
    Calcula la ruta más corta entre dos nodos (cantones) en un grafo ponderado.

    Args:
        grafo (dict): El grafo sobre el cual se ejecutará el algoritmo.
        origen (str): El cantón de inicio.
        destino (str): El cantón de destino.

    Returns:
        tuple: Una tupla con (distancia_total, lista_de_cantones_en_la_ruta, tipos_de_tramo).
               Si no se encuentra una ruta, devuelve (inf, [], []).
    """
    # Conjunto para almacenar los nodos ya visitados y no volver a procesarlos.
    visitados = set()
    # Cola de prioridad (min-heap) para seleccionar siempre el nodo con menor costo.
    # Estructura de la tupla: (costo_acumulado, nodo_actual, camino_recorrido, tipos_de_tramo)
    heap = [(0, origen, [origen], [])]

    while heap:
        # Extrae el nodo con el menor costo acumulado de la cola.
        (costo, actual, camino, tipos) = heappop(heap)

        # Si el nodo actual es el destino, hemos encontrado la ruta más corta.
        if actual == destino:
            return costo, camino, tipos

        # Si ya hemos visitado este nodo con una ruta más corta, lo ignoramos.
        if actual in visitados:
            continue
        
        # Marcamos el nodo actual como visitado.
        visitados.add(actual)

        # Exploramos los vecinos del nodo actual.
        for vecino, data in grafo.get(actual, {}).items():
            if vecino not in visitados:
                # Añadimos el vecino a la cola con el costo actualizado y el camino extendido.
                nuevo_costo = costo + data['distancia']
                nuevo_camino = camino + [vecino]
                nuevos_tipos = tipos + [data['tipo']]
                heappush(heap, (nuevo_costo, vecino, nuevo_camino, nuevos_tipos))
    
    # Si el bucle termina y no se encontró el destino, no hay una ruta posible.
    return float('inf'), [], []

