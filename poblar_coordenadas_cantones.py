# =================== Script para Poblar Coordenadas de Cantones ===================
# Este script se utiliza para obtener y guardar las coordenadas (latitud y longitud)
# de los cantones almacenados en la base de datos que aún no las tienen.
# Utiliza la API pública de Nominatim (OpenStreetMap) para la geocodificación.
#
# IMPORTANTE: Ejecutar este script con precaución, ya que realiza múltiples
# peticiones a una API externa y modifica la base de datos.

# =================== Importaciones ===================
import requests  # Para realizar peticiones HTTP a la API de Nominatim.
from app import app, db  # Importa la aplicación Flask y la instancia de la base de datos.
from app.models import Canton, Provincia  # Importa los modelos necesarios.
import time  # Para añadir pausas entre peticiones y respetar los límites de la API.

# =================== Constantes de Configuración ===================
# URL del servicio de búsqueda de Nominatim.
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
# User-Agent requerido por la política de uso de Nominatim para identificar la aplicación.
USER_AGENT = "AgrogridCantonGeocoder/1.0 (contacto@agrogrid.local)"


def obtener_coordenadas(nombre_canton, nombre_provincia, pais="Ecuador"):
    """
    Realiza una petición a la API de Nominatim para obtener las coordenadas de un lugar.

    Args:
        nombre_canton (str): El nombre del cantón a buscar.
        nombre_provincia (str): El nombre de la provincia para dar contexto a la búsqueda.
        pais (str, optional): El país para acotar la búsqueda. Por defecto es "Ecuador".

    Returns:
        tuple: Una tupla (latitud, longitud) si se encuentra, o (None, None) si no.
    """
    # Parámetros para la petición GET a la API.
    params = {
        'q': f"{nombre_canton}, {nombre_provincia}, {pais}",  # La consulta de búsqueda.
        'format': 'json',  # Se solicita la respuesta en formato JSON.
        'limit': 1  # Se limita a un solo resultado, el más relevante.
    }
    headers = {'User-Agent': USER_AGENT}  # Cabecera necesaria para la autenticación.
    
    try:
        resp = requests.get(NOMINATIM_URL, params=params, headers=headers, timeout=10)
        # Si la respuesta es exitosa (código 200) y contiene datos.
        if resp.status_code == 200 and resp.json():
            data = resp.json()[0]
            return float(data['lat']), float(data['lon'])
    except requests.exceptions.RequestException as e:
        print(f"Error en la petición a Nominatim: {e}")

    return None, None


def poblar_coordenadas():
    """
    Itera sobre todos los cantones en la base de datos, obtiene las coordenadas
    para aquellos que no las tienen y actualiza los registros.
    """
    # Se utiliza el contexto de la aplicación para poder acceder a la base de datos.
    with app.app_context():
        cantones = Canton.query.all()
        print(f"Iniciando proceso para {len(cantones)} cantones...")

        for canton in cantones:
            # Si el cantón ya tiene coordenadas, se omite.
            if canton.lat is not None and canton.lon is not None:
                print(f"{canton.nombre}: ya tiene coordenadas. Omitiendo...")
                continue
            
            # Se obtiene el nombre de la provincia para la búsqueda.
            provincia = Provincia.query.get(canton.provincia_id)
            if not provincia:
                print(f"Error: No se encontró provincia para el cantón {canton.nombre}. Omitiendo...")
                continue

            print(f"Buscando coordenadas para: {canton.nombre}, {provincia.nombre}")
            lat, lon = obtener_coordenadas(canton.nombre, provincia.nombre)
            
            if lat and lon:
                # Si se encontraron coordenadas, se actualiza el objeto Canton.
                canton.lat = lat
                canton.lon = lon
                db.session.commit()  # Se guardan los cambios en la base de datos.
                print(f"-> ¡Éxito! Coordenadas para {canton.nombre} guardadas: lat={lat}, lon={lon}")
            else:
                print(f"-> No se encontraron coordenadas para: {canton.nombre}, {provincia.nombre}")
            
            # Pausa de 1 segundo para cumplir con la política de uso de Nominatim (máx 1 req/seg).
            time.sleep(1)

# Punto de entrada para ejecutar el script directamente desde la línea de comandos.
if __name__ == "__main__":
    print("====================================================")
    print("Poblando coordenadas de cantones desde Nominatim...")
    print("====================================================")
    poblar_coordenadas()
    print("====================================================")
    print("Proceso finalizado.")
    print("====================================================")
