# =================== Lógica de Ubicación Geográfica ===================
# Este módulo se encarga de construir la estructura jerárquica de ubicaciones
# de Ecuador (Región > Provincia > Cantón) a partir de la base de datos.

# =================== Importaciones locales ===================
from app.models import Region, Provincia, Canton  # Importa los modelos de la base de datos para las ubicaciones.

# =================== Funciones de Ubicación ===================
def obtener_estructura_ubicacion():
    """
    Construye y devuelve una estructura anidada de ubicaciones geográficas de Ecuador.
    La estructura se obtiene consultando las tablas Region, Provincia y Canton en la base de datos
    y se ordena alfabéticamente en cada nivel.

    El formato de salida es:
    { 'NombreRegion': { 'NombreProvincia': ['Canton1', 'Canton2', ...] } }

    Returns:
        dict: Un diccionario que representa la jerarquía completa de ubicaciones.
    """
    # Diccionario que contendrá la estructura final.
    estructura = {}
    
    # 1. Obtener todas las regiones de la base de datos, ordenadas por nombre.
    regiones = Region.query.order_by(Region.nombre).all()
    
    # 2. Iterar sobre cada región para procesar sus provincias.
    for region in regiones:
        provincias_dict = {}  # Diccionario para las provincias y cantones de la región actual.
        
        # 3. Obtener las provincias de la región actual y ordenarlas por nombre.
        # Se usa sorted() en lugar de .order_by() porque 'provincias' es una relación de SQLAlchemy.
        provincias = sorted(region.provincias, key=lambda p: p.nombre)
        
        # 4. Iterar sobre cada provincia para procesar sus cantones.
        for provincia in provincias:
            # 5. Obtener los nombres de los cantones de la provincia actual y ordenarlos alfabéticamente.
            cantones = sorted([c.nombre for c in provincia.cantones])
            # Asignar la lista de cantones a su respectiva provincia.
            provincias_dict[provincia.nombre] = cantones
            
        # 6. Asignar el diccionario de provincias a su respectiva región.
        estructura[region.nombre] = provincias_dict
        
    return estructura

