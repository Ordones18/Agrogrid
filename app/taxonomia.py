from app.models import Categoria, Subcategoria

def obtener_estructura_taxonomia():
    """
    Devuelve la estructura de taxonomía de 3 niveles:
    {
        'Categoria': {
            'Subcategoria2 (padre=None)': [ 'Subcategoria3', ... ]
        }
    }
    Si Subcategoria2 no tiene hijos, la lista es vacía.
    """
    estructura = {}
    categorias = Categoria.query.order_by(Categoria.nombre).all()
    for categoria in categorias:
        subcat2_dict = {}
        # Subcategoría nivel 2: las que no tienen padre (padre=None)
        subcats2 = Subcategoria.query.filter_by(categoria_id=categoria.id, parent_id=None).order_by(Subcategoria.nombre).all()
        for subcat2 in subcats2:
            # Subcategoría nivel 3: hijas de subcat2
            subcats3 = Subcategoria.query.filter_by(parent_id=subcat2.id).order_by(Subcategoria.nombre).all()
            subcats3_nombres = [s.nombre for s in subcats3]
            subcat2_dict[subcat2.nombre] = subcats3_nombres
        estructura[categoria.nombre] = subcat2_dict
    return estructura

def obtener_taxonomia_catalogo():
    # Alias para compatibilidad con imports viejos
    return obtener_estructura_taxonomia()
