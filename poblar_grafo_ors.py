# =================== Script para Generar Grafo Geodésico ===================
#
# Este script genera un grafo de transporte completo entre todos los cantones de Ecuador
# que tengan coordenadas en la base de datos.
#
# Funcionamiento:
# 1. Carga todos los cantones desde la base de datos.
# 2. Para cada par de cantones, calcula la distancia geodésica (en línea recta)
#    entre sus coordenadas (latitud, longitud).
# 3. Estima el tiempo de viaje basándose en una velocidad promedio constante.
# 4. Guarda el grafo resultante en un archivo JSON, que puede ser utilizado
#    por el sistema de cálculo de rutas.
#
# Nota: Este grafo es una aproximación, ya que no considera rutas reales
# (carreteras, obstáculos geográficos, etc.). Es útil como una base o para
# casos donde no se dispone de un servicio de enrutamiento avanzado.
#
# =================== Importaciones ===================
import json  # Para la manipulación y guardado de datos en formato JSON.
from geopy.distance import geodesic  # Para calcular la distancia en línea recta entre dos puntos geográficos.
from app import app  # Importa la instancia de la aplicación Flask para obtener el contexto.
from app.models import Canton  # Importa el modelo Canton para acceder a los datos de la BD.

# =================== Constantes ===================
# Velocidad promedio en km/h usada para estimar el tiempo de viaje.
VELOCIDAD_PROMEDIO = 60


def poblar_grafo_geodesico(salida_json="grafo_cantonal_geodesico.json"):
    """
    Crea un grafo completo con distancias geodésicas y tiempos estimados
    entre todos los cantones y lo guarda en un archivo JSON.

    Args:
        salida_json (str, optional): El nombre del archivo JSON de salida.
                                     Por defecto es "grafo_cantonal_geodesico.json".
    """
    # Se utiliza el contexto de la aplicación para poder interactuar con la base de datos.
    with app.app_context():
        # 1. Obtener todos los cantones de la base de datos.
        cantones = Canton.query.all()
        # Filtrar solo aquellos cantones que tienen coordenadas válidas.
        nodos = [(c.nombre, c.lat, c.lon) for c in cantones if c.lat is not None and c.lon is not None]
        
        grafo = {}
        total = len(nodos)
        print(f"Generando grafo para {total} cantones con coordenadas...")

        # 2. Iterar sobre cada par de cantones para calcular la distancia y el tiempo.
        for i, (nombre_origen, lat1, lon1) in enumerate(nodos):
            grafo[nombre_origen] = {}
            for j, (nombre_destino, lat2, lon2) in enumerate(nodos):
                # No se calcula la distancia de un cantón a sí mismo.
                if nombre_origen == nombre_destino:
                    continue
                
                # 3. Calcular la distancia geodésica en kilómetros.
                distancia_km = geodesic((lat1, lon1), (lat2, lon2)).km
                # Estimar el tiempo de viaje en horas.
                tiempo_horas = distancia_km / VELOCIDAD_PROMEDIO
                
                # 4. Añadir la arista al grafo con sus propiedades.
                grafo[nombre_origen][nombre_destino] = {
                    'distancia': round(distancia_km, 2),
                    'tiempo': round(tiempo_horas * 60, 2),  # Convertir tiempo a minutos.
                    'tipo': 'terrestre'  # Se asume que todas las rutas son terrestres.
                }
            
            # Imprimir el progreso del proceso.
            print(f"Procesado cantón {i + 1}/{total}: {nombre_origen}")

        # 5. Guardar el grafo completo en un archivo JSON.
        with open(salida_json, 'w', encoding='utf-8') as f:
            # json.dump para escribir el diccionario en el archivo.
            # ensure_ascii=False para permitir caracteres como tildes.
            # indent=2 para que el JSON sea legible.
            json.dump(grafo, f, ensure_ascii=False, indent=2)
        
        print(f"\n¡Éxito! Grafo geodésico guardado en '{salida_json}'")


# Punto de entrada para ejecutar el script directamente.
if __name__ == "__main__":
    print("======================================================")
    print("Iniciando la generación del grafo de cantones...")
    print("======================================================")
    poblar_grafo_geodesico()
    print("======================================================")
    print("Proceso de generación de grafo finalizado.")
    print("======================================================")


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
