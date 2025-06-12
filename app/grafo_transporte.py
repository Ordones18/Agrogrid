from heapq import heappush, heappop
from typing import Dict, Tuple, List
import os
import json
from app.models import Canton
from app import app

grafo_cantonal = {}

# Estructura: {canton: {vecino: {'distancia': km, 'tipo': 'terrestre'/'maritimo'}}}
def generar_grafo_completo_cantones(distancia_fija=100, tipo='terrestre'):
    """
    Genera un grafo completo conectando todos los cantones de la BD entre sí 
    """
    grafo = {}
    with app.app_context():
        cantones = [c.nombre for c in Canton.query.all()]
        for origen in cantones:
            grafo[origen] = {}
            for destino in cantones:
                if origen != destino:
                    grafo[origen][destino] = {'distancia': distancia_fija, 'tipo': tipo}
    return grafo

# Poblar el grafo_cantonal automáticamente al iniciar el módulo desde el archivo geodésico generado

GRAFO_JSON_PATH = os.path.join(os.path.dirname(__file__), '..', 'grafo_cantonal_vecinos.json')
try:
    with open(GRAFO_JSON_PATH, 'r', encoding='utf-8') as f:
        grafo_cantonal = json.load(f)
    print(f"[INFO] Grafo cantonal cargado desde {GRAFO_JSON_PATH}")
except FileNotFoundError:
    print(f"[ADVERTENCIA] No se encontró {GRAFO_JSON_PATH}. El grafo_cantonal está vacío.")
    grafo_cantonal = {}

def dijkstra(grafo: Dict[str, Dict[str, Dict]], origen: str, destino: str) -> Tuple[float, List[str], List[str]]:
    """
    Calcula la ruta más corta entre dos cantones usando Dijkstra.
    Retorna la distancia total, el camino (lista de cantones) y los tipos de tramo (terrestre/maritimo).
    """
    visitados = set()
    heap = [(0, origen, [origen], [])]  # (costo, actual, camino, tipos)
    while heap:
        (costo, actual, camino, tipos) = heappop(heap)
        if actual == destino:
            return costo, camino, tipos
        if actual in visitados:
            continue
        visitados.add(actual)
        for vecino, data in grafo.get(actual, {}).items():
            if vecino not in visitados:
                heappush(heap, (costo + data['distancia'], vecino, camino + [vecino], tipos + [data['tipo']]))
    return float('inf'), [], []



# Ejemplo de uso:
# distancia, ruta = dijkstra(grafo_cantonal, 'Quito', 'Ambato')
# print(f"Distancia: {distancia} km, Ruta: {' -> '.join(ruta)}")
