# =================== Script para Visualizar Estructura de la BD ===================
#
# Este script de utilidad sirve para inspeccionar y entender la estructura jerárquica
# de los datos de ubicación (Región, Provincia, Cantón) y de catálogo (Categoría,
# Subcategoría, Producto) tal como están almacenados en la base de datos.
#
# Funcionalidades:
# 1. Muestra en la consola un árbol de la jerarquía de ubicaciones.
# 2. Muestra en la consola un árbol de la jerarquía del catálogo de productos.
# 3. Opcionalmente, exporta la estructura de ubicaciones a un archivo CSV.
#
# Uso:
# - Para ver las estructuras en consola: `python ver_bd_estructura.py`
# - Para ver y además exportar a CSV: `python ver_bd_estructura.py --csv`
#
# =================== Importaciones ===================
from app import app
from app.models import Region, Provincia, Canton, Categoria, Subcategoria, Producto
import csv
import sys


def mostrar_ubicacion():
    """Consulta y muestra en consola la jerarquía de ubicaciones."""
    print("\n===========================================")
    print("--- Estructura de Ubicaciones (Región > Provincia > Cantón) ---")
    print("===========================================")
    regiones = Region.query.all()
    for region in regiones:
        print(f"Región: {region.nombre}")
        for provincia in sorted(region.provincias, key=lambda x: x.nombre):
            print(f'  Provincia: {provincia.nombre}')
            for canton in sorted(provincia.cantones, key=lambda x: x.nombre):
                print(f'    Cantón: {canton.nombre}')


def mostrar_categorias():
    """Consulta y muestra en consola la jerarquía del catálogo de productos."""
    print("\n===========================================")
    print("--- Estructura de Catálogo (Categoría > Subcategoría > Producto) ---")
    print("===========================================")
    categorias = Categoria.query.all()
    for categoria in categorias:
        print(f'Categoría: {categoria.nombre}')
        for subcat in sorted(categoria.subcategorias, key=lambda x: x.nombre):
            print(f'  Subcategoría: {subcat.nombre}')
            # Se consultan los productos para cada subcategoría.
            productos = Producto.query.filter_by(subcategoria_id=subcat.id).all()
            for producto in sorted(productos, key=lambda x: x.nombre):
                print(f'    Producto: {producto.nombre}')


def exportar_cantones_csv(path_csv='cantones.csv'):
    """
    Exporta la estructura jerárquica de ubicaciones a un archivo CSV.

    Args:
        path_csv (str, optional): El nombre del archivo de salida. Por defecto 'cantones.csv'.
    """
    print("\n===========================================")
    print(f"Exportando estructura de cantones a '{path_csv}'...")
    with open(path_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        # Escribir la fila de encabezado.
        writer.writerow(['Region', 'Provincia', 'Canton'])
        regiones = Region.query.all()
        # Iterar a través de la jerarquía y escribir cada cantón en una nueva fila.
        for region in regiones:
            for provincia in region.provincias:
                for canton in provincia.cantones:
                    writer.writerow([region.nombre, provincia.nombre, canton.nombre])
    print(f"¡Éxito! Archivo CSV generado en '{path_csv}'")


# =================== Punto de Entrada del Script ===================
if __name__ == '__main__':
    # Se utiliza el contexto de la aplicación para poder interactuar con la base de datos.
    with app.app_context():
        # Siempre se muestran las estructuras en la consola.
        mostrar_ubicacion()
        mostrar_categorias()
        
        # Se comprueba si el argumento '--csv' fue pasado en la línea de comandos.
        if '--csv' in sys.argv:
            # Si es así, se llama a la función de exportación.
            exportar_cantones_csv()
