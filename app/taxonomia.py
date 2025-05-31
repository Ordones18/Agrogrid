# =================== TAXONOMÍA DE PRODUCTOS AGRÍCOLAS ===================
# Sistema de clasificación jerárquica para productos agrícolas ecuatorianos

TAXONOMIA_PRODUCTOS = {
    "frutas": {
        "label": "Frutas",
        "icon": "🍎",
        "subcategorias": {
            "citricas": {
                "label": "Cítricas",
                "icon": "🍊",
                "productos": [
                    "Naranja",
                    "Limón",
                    "Mandarina",
                    "Lima",
                    "Toronja"
                ]
            },
            "tropicales": {
                "label": "Tropicales",
                "icon": "🥭",
                "productos": [
                    "Banano",
                    "Mango",
                    "Piña",
                    "Papaya",
                    "Coco",
                    "Guayaba"
                ]
            },
            "clima_frio": {
                "label": "De Clima Frío",
                "icon": "🍓",
                "productos": [
                    "Fresa",
                    "Mora",
                    "Tomate de árbol",
                    "Uvilla",
                    "Babaco"
                ]
            },
            "exoticas": {
                "label": "Exóticas",
                "icon": "🫐",
                "productos": [
                    "Naranjilla",
                    "Maracuyá",
                    "Pitahaya",
                    "Borojó",
                    "Arazá"
                ]
            }
        }
    },
    "vegetales": {
        "label": "Vegetales/Hortalizas",
        "icon": "🥬",
        "subcategorias": {
            "hojas_verdes": {
                "label": "Hojas Verdes",
                "icon": "🥬",
                "productos": [
                    "Lechuga",
                    "Espinaca",
                    "Acelga",
                    "Col",
                    "Apio"
                ]
            },
            "cruciferas": {
                "label": "Crucíferas",
                "icon": "🥦",
                "productos": [
                    "Brócoli",
                    "Coliflor",
                    "Col de Bruselas",
                    "Rábano"
                ]
            },
            "raices": {
                "label": "Raíces",
                "icon": "🥕",
                "productos": [
                    "Zanahoria",
                    "Remolacha",
                    "Nabo"
                ]
            },
            "bulbos": {
                "label": "Bulbos",
                "icon": "🧅",
                "productos": [
                    "Cebolla paiteña",
                    "Cebolla perla",
                    "Ajo",
                    "Cebollín",
                    "Puerro"
                ]
            },
            "frutos": {
                "label": "Frutos",
                "icon": "🍅",
                "productos": [
                    "Tomate riñón",
                    "Tomate cherry",
                    "Pimiento",
                    "Ají",
                    "Pepino",
                    "Calabacín"
                ]
            }
        }
    },
    "tuberculos": {
        "label": "Tubérculos",
        "icon": "🥔",
        "subcategorias": {
            "papa": {
                "label": "Papa",
                "icon": "🥔",
                "productos": [
                    "Papa chola",
                    "Papa súper chola",
                    "Papa única",
                    "Papa bolona",
                    "Papa capiro"
                ]
            },
            "yuca": {
                "label": "Yuca",
                "icon": "🍠",
                "productos": [
                    "Yuca blanca",
                    "Yuca amarilla"
                ]
            },
            "camote": {
                "label": "Camote",
                "icon": "🍯",
                "productos": [
                    "Camote morado",
                    "Camote amarillo",
                    "Camote blanco"
                ]
            },
            "otros": {
                "label": "Otros Tubérculos",
                "icon": "🌱",
                "productos": [
                    "Oca",
                    "Melloco",
                    "Mashua"
                ]
            }
        }
    },
    "granos": {
        "label": "Granos/Cereales",
        "icon": "🌾",
        "subcategorias": {
            "maiz": {
                "label": "Maíz",
                "icon": "🌽",
                "productos": [
                    "Maíz duro seco",
                    "Maíz suave",
                    "Maíz dulce",
                    "Choclo"
                ]
            },
            "quinoa": {
                "label": "Quinoa",
                "icon": "🌾",
                "productos": [
                    "Quinoa blanca",
                    "Quinoa roja",
                    "Quinoa negra",
                    "Quinoa tricolor"
                ]
            },
            "leguminosas": {
                "label": "Leguminosas",
                "icon": "🫘",
                "productos": [
                    "Fréjol negro",
                    "Fréjol rojo",
                    "Fréjol blanco",
                    "Arveja",
                    "Haba",
                    "Lenteja"
                ]
            },
            "cacao": {
                "label": "Cacao",
                "icon": "🍫",
                "productos": [
                    "Cacao nacional",
                    "Cacao CCN-51",
                    "Cacao trinitario"
                ]
            },
            "arroz": {
                "label": "Arroz",
                "icon": "🌾",
                "productos": [
                    "Arroz en cáscara",
                    "Arroz pilado"
                ]
            }
        }
    },
    "especias": {
        "label": "Especias/Aromáticas",
        "icon": "🌿",
        "subcategorias": {
            "culinarias": {
                "label": "Culinarias",
                "icon": "🌿",
                "productos": [
                    "Culantro",
                    "Perejil",
                    "Albahaca",
                    "Orégano",
                    "Tomillo",
                    "Hierba buena",
                    "Menta"
                ]
            },
            "condimentos": {
                "label": "Condimentos",
                "icon": "🌶️",
                "productos": [
                    "Ají rocoto",
                    "Ají habanero",
                    "Comino",
                    "Anís"
                ]
            }
        }
    }
}

def obtener_productos_planos():
    """
    Retorna una lista plana de todos los productos disponibles
    con su categorización completa para búsquedas
    """
    productos = []
    
    for cat_key, categoria in TAXONOMIA_PRODUCTOS.items():
        for subcat_key, subcategoria in categoria["subcategorias"].items():
            for producto in subcategoria["productos"]:
                productos.append({
                    "nombre": producto,
                    "categoria": categoria["label"],
                    "subcategoria": subcategoria["label"],
                    "categoria_key": cat_key,
                    "subcategoria_key": subcat_key,
                    "path": f"{categoria['label']} > {subcategoria['label']} > {producto}"
                })
    
    return productos

def buscar_productos(termino):
    """
    Busca productos por término de búsqueda
    """
    productos = obtener_productos_planos()
    termino = termino.lower()
    
    resultados = []
    for producto in productos:
        if (termino in producto["nombre"].lower() or 
            termino in producto["categoria"].lower() or 
            termino in producto["subcategoria"].lower()):
            resultados.append(producto)
    
    return resultados

def obtener_estructura_simple():
    """
    Convierte la estructura compleja de TAXONOMIA_PRODUCTOS a la estructura simple 
    que espera el JavaScript: {categoria: {subcategoria: [productos]}}
    """
    estructura_simple = {}
    
    for cat_key, categoria in TAXONOMIA_PRODUCTOS.items():
        categoria_label = categoria["label"]
        estructura_simple[categoria_label] = {}
        
        for subcat_key, subcategoria in categoria["subcategorias"].items():
            subcategoria_label = subcategoria["label"]
            estructura_simple[categoria_label][subcategoria_label] = subcategoria["productos"]
    
    return estructura_simple

def obtener_iconos_categorias():
    """
    Devuelve un diccionario con los íconos de las categorías principales
    """
    iconos = {}
    for cat_key, categoria in TAXONOMIA_PRODUCTOS.items():
        iconos[categoria["label"]] = categoria["icon"]
    return iconos
