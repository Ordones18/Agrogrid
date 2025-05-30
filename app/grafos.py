import networkx as nx

# =================== GRAFOS DE PRODUCTOS ===================
def construir_grafo_productos(productos):
    """
    Construye un grafo donde cada nodo es un producto y hay aristas entre productos que comparten tipo o región.
    Recibe una lista de productos (objetos SQLAlchemy).
    Devuelve el grafo de NetworkX.
    """
    G = nx.Graph()
    # Agregar nodos
    for p in productos:
        G.add_node(p.id, nombre=p.nombre, tipo=p.tipo, region=p.region, provincia=p.provincia, precio=p.precio, cantidad=p.cantidad, unidad=p.unidad)
    # Agregar aristas por tipo o región
    for i, p1 in enumerate(productos):
        for j, p2 in enumerate(productos):
            if i >= j:
                continue
            if p1.tipo == p2.tipo or p1.region == p2.region:
                G.add_edge(p1.id, p2.id)
    return G

# Aquí puedes agregar más funciones de análisis, búsqueda, recomendaciones, etc. 