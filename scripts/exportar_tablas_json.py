import json
from app import db
from app.models import Region, Provincia, Canton, Categoria, Subcategoria
from app import app

def exportar_tabla(modelo, nombre):
    datos = [fila.__dict__.copy() for fila in db.session.query(modelo).all()]
    for d in datos:
        d.pop('_sa_instance_state', None)
    with open(f"export_{nombre}.json", 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
    print(f"Exportado: export_{nombre}.json")

if __name__ == "__main__":
    with app.app_context():
        exportar_tabla(Region, 'region')
        exportar_tabla(Provincia, 'provincia')
        exportar_tabla(Canton, 'canton')
        exportar_tabla(Categoria, 'categoria')
        exportar_tabla(Subcategoria, 'subcategoria')
