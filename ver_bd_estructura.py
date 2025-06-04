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
            productos = subcat.productos
            for producto in productos:
                print(f'    Producto: {producto.nombre}')

if __name__ == '__main__':
    with app.app_context():
        mostrar_ubicacion()
        mostrar_categorias()

# ver la estructura de la base de datos para la ubicación y el catalogo de productos a agregar
# python ver_bd_estructura.py


