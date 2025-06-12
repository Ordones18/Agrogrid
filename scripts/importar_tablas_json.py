import json
from app import db
from app.models import Region, Provincia, Canton, Categoria, Subcategoria

def importar_tabla(modelo, archivo):
    with open(archivo, 'r', encoding='utf-8') as f:
        datos = json.load(f)
    for d in datos:
        obj = modelo(**d)
        db.session.add(obj)
    db.session.commit()
    print(f"Importados {len(datos)} registros en {modelo.__name__}")

if __name__ == "__main__":
    importar_tabla(Region, 'export_region.json')
    importar_tabla(Provincia, 'export_provincia.json')
    importar_tabla(Canton, 'export_canton.json')
    importar_tabla(Categoria, 'export_categoria.json')
    importar_tabla(Subcategoria, 'export_subcategoria.json')

