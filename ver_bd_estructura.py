from app import app
from app.models import Region, Provincia, Canton, Categoria, Subcategoria, Producto


def mostrar_ubicacion():
    print('--- UBICACIÓN ---')
    regiones = Region.query.all()
    for region in regiones:
        print(f'Región: {region.nombre}')
        for provincia in region.provincias:
            print(f'  Provincia: {provincia.nombre}')
            for canton in provincia.cantones:
                print(f'    Cantón: {canton.nombre}')


def mostrar_categorias():
    print('\n--- CATEGORÍAS, SUBCATEGORÍAS Y PRODUCTOS EN BD ---')
    categorias = Categoria.query.all()
    for categoria in categorias:
        print(f'Categoría: {categoria.nombre}')
        for subcat in categoria.subcategorias:
            print(f'  Subcategoría: {subcat.nombre}')
            from app.models import Producto
            productos = Producto.query.filter_by(subcategoria_id=subcat.id).all()
            for producto in productos:
                print(f'    Producto: {producto.nombre}')

import csv
import sys

def exportar_cantones_csv(path_csv='cantones.csv'):
    with open(path_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Region', 'Provincia', 'Canton'])
        regiones = Region.query.all()
        for region in regiones:
            for provincia in region.provincias:
                for canton in provincia.cantones:
                    writer.writerow([region.nombre, provincia.nombre, canton.nombre])
    print(f'Archivo CSV generado: {path_csv}')

if __name__ == '__main__':
    with app.app_context():
        mostrar_ubicacion()
        mostrar_categorias()
        if '--csv' in sys.argv:
            exportar_cantones_csv()

# ver la estructura de la base de datos para la ubicación y el catalogo de productos a agregar
# python ver_bd_estructura.py
# Para exportar a CSV: python ver_bd_estructura.py --csv
