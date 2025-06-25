# =================== Importaciones locales ===================
from app.models import Categoria, Subcategoria  # Importa los modelos para consultar la jerarquía de categorías.

# =================== Lógica de Taxonomía ===================

def obtener_estructura_taxonomia():
    """
    Construye y devuelve una estructura jerárquica de taxonomía de hasta 3 niveles.
    La estructura tiene el formato: { Categoria: { Subcategoria_Nivel_2: [Subcategorias_Nivel_3] } }

    - Nivel 1: Categorías principales (e.g., 'FRUTAS').
    - Nivel 2: Subcategorías que no tienen padre (parent_id=None).
    - Nivel 3: Subcategorías que son hijas de una subcategoría de Nivel 2.

    Si una subcategoría de Nivel 2 no tiene hijas, su valor será una lista vacía.

    Returns:
        dict: Un diccionario que representa la taxonomía completa de productos.
    """
    # Diccionario principal que almacenará la estructura final.
    estructura = {}
    
    # 1. Obtener todas las categorías principales, ordenadas alfabéticamente.
    categorias = Categoria.query.order_by(Categoria.nombre).all()
    
    # 2. Iterar sobre cada categoría para construir su sub-estructura.
    for categoria in categorias:
        subcat2_dict = {}  # Diccionario para las subcategorías de nivel 2 y sus hijas.
        
        # 3. Obtener las subcategorías de nivel 2 (aquellas sin un 'padre' o 'parent_id').
        subcats2 = Subcategoria.query.filter_by(categoria_id=categoria.id, parent_id=None).order_by(Subcategoria.nombre).all()
        
        # 4. Iterar sobre cada subcategoría de nivel 2 para encontrar sus hijas (nivel 3).
        for subcat2 in subcats2:
            # 5. Obtener las subcategorías de nivel 3, que son hijas de la subcategoría actual.
            subcats3 = Subcategoria.query.filter_by(parent_id=subcat2.id).order_by(Subcategoria.nombre).all()
            # Extraer solo los nombres de las subcategorías de nivel 3.
            subcats3_nombres = [s.nombre for s in subcats3]
            
            # Asignar la lista de nombres de nivel 3 a su padre de nivel 2.
            subcat2_dict[subcat2.nombre] = subcats3_nombres
            
        # Asignar el diccionario de subcategorías a la categoría principal.
        estructura[categoria.nombre] = subcat2_dict
        
    return estructura

def obtener_taxonomia_catalogo():
    """
    Función alias para mantener la compatibilidad con partes del código que
    puedan estar usando este nombre. Llama directamente a obtener_estructura_taxonomia().
    
    Returns:
        dict: La misma estructura devuelta por obtener_estructura_taxonomia().
    """
    # Se retorna el resultado de la función principal para no duplicar código.
    return obtener_estructura_taxonomia()
