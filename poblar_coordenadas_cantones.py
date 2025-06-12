import requests
from app import app, db
from app.models import Canton, Provincia
import time

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "AgrogridCantonGeocoder/1.0 (contacto@agrogrid.local)"


def obtener_coordenadas(nombre_canton, nombre_provincia, pais="Ecuador"):
    params = {
        'q': f"{nombre_canton}, {nombre_provincia}, {pais}",
        'format': 'json',
        'limit': 1
    }
    headers = {'User-Agent': USER_AGENT}
    resp = requests.get(NOMINATIM_URL, params=params, headers=headers, timeout=10)
    if resp.status_code == 200 and resp.json():
        data = resp.json()[0]
        return float(data['lat']), float(data['lon'])
    return None, None


def poblar_coordenadas():
    with app.app_context():
        cantones = Canton.query.all()
        for canton in cantones:
            if canton.lat is not None and canton.lon is not None:
                print(f"{canton.nombre}: ya tiene coordenadas.")
                continue
            provincia = Provincia.query.get(canton.provincia_id)
            print(f"Buscando coordenadas para: {canton.nombre}, provincia: {provincia.nombre}")
            lat, lon = obtener_coordenadas(canton.nombre, provincia.nombre)
            if lat and lon:
                canton.lat = lat
                canton.lon = lon
                db.session.commit()
                print(f"OK {canton.nombre}: lat={lat}, lon={lon}")
            else:
                print(f"No encontrado: {canton.nombre}, provincia: {provincia.nombre}")
            time.sleep(1)  # Respetar el rate limit de Nominatim

if __name__ == "__main__":
    poblar_coordenadas()
