# ubicacion.py
# Árbol de clasificación de ubicación para Ecuador: Región > Provincia > Cantón
# Ahora la estructura se obtiene directamente desde la base de datos

from app.models import Region, Provincia, Canton
def obtener_estructura_ubicacion():
    """
    Devuelve la estructura de ubicación {region: {provincia: [cantones]}} directamente desde la BD, todo ordenado alfabéticamente.
    """
    estructura = {}
    regiones = Region.query.order_by(Region.nombre).all()
    for region in regiones:
        provincias_dict = {}
        provincias = sorted(region.provincias, key=lambda p: p.nombre)
        for provincia in provincias:
            cantones = sorted([c.nombre for c in provincia.cantones])
            provincias_dict[provincia.nombre] = cantones
        estructura[region.nombre] = provincias_dict
    return estructura

# Si necesitas guardar la selección en la base de datos, puedes usar estos nombres de campo:
# region, provincia, canton
