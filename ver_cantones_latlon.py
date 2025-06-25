# =================== Script para Verificar Coordenadas de Cantones ===================
#
# Este script de utilidad se conecta a la base de datos para listar todos los cantones
# junto con sus coordenadas (latitud y longitud), si es que las tienen.
#
# Funcionalidades:
# 1. Muestra una tabla formateada con el ID, Nombre, Latitud y Longitud de cada cantón.
# 2. Al final, presenta un resumen del número de cantones que tienen coordenadas
#    y cuántos aún no las tienen.
#
# Es especialmente útil para verificar el resultado del script `poblar_coordenadas_cantones.py`.
#
# Uso: `python ver_cantones_latlon.py`
#
# =================== Importaciones ===================
from app import app          # Importa la instancia de la aplicación Flask para obtener el contexto.
from app.models import Canton  # Importa el modelo Canton para interactuar con la tabla de cantones.

# =================== Lógica de Visualización ===================
# Se utiliza el contexto de la aplicación para poder interactuar con la base de datos.
with app.app_context():
    # 1. Consultar todos los cantones de la base de datos, ordenados alfabéticamente por nombre.
    cantones = Canton.query.order_by(Canton.nombre).all()

    # 2. Imprimir una cabecera de tabla bien formateada.
    print("\n================== Listado de Cantones y Coordenadas ==================")
    print(f"{'ID':<5} {'Nombre':<30} {'Latitud':<20} {'Longitud':<20}")
    print("-" * 75)

    # 3. Iterar sobre cada cantón y mostrar su información.
    for canton in cantones:
        # Formatear la latitud y longitud para que se muestren como 'N/A' si son None.
        lat_str = str(round(canton.lat, 6)) if canton.lat is not None else 'N/A'
        lon_str = str(round(canton.lon, 6)) if canton.lon is not None else 'N/A'
        # Imprimir la fila de datos del cantón, alineada con la cabecera.
        print(f"{canton.id:<5} {canton.nombre:<30} {lat_str:<20} {lon_str:<20}")

    # 4. Calcular y mostrar un resumen estadístico.
    print("\n================== Resumen ==================")
    con_coords = sum(1 for c in cantones if c.lat is not None and c.lon is not None)
    sin_coords = len(cantones) - con_coords
    print(f"Total de cantones: {len(cantones)}")
    print(f"Cantones CON coordenadas: {con_coords}")
    print(f"Cantones SIN coordenadas: {sin_coords}")
    print("=========================================")
