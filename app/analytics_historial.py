# Se importa la librería pandas, fundamental para el análisis y manipulación de datos.
import pandas as pd

def preparar_historial_ventas(orden_items, producto_map):
    """
    Procesa los datos de ventas para generar un historial estructurado.

    Args:
        orden_items (list): Una lista de tuplas que contienen objetos (OrdenItem, Orden).
        producto_map (dict): Un diccionario que mapea ID de productos a sus nombres.

    Returns:
        list: Una lista de diccionarios, donde cada diccionario representa una venta.
              La lista está ordenada por fecha de forma descendente.
              Devuelve una lista vacía si no hay datos de ventas.
    """
    # Lista para almacenar los datos procesados de cada venta.
    data = []
    # Importación local para evitar dependencias circulares.
    from app.models import Usuario

    # Itera sobre cada ítem de orden y su orden correspondiente.
    for item, orden in orden_items:
        # Obtiene de forma segura el nombre del comprador.
        # Primero intenta acceder a través de la relación 'comprador' cargada.
        comprador_nombre = None
        if hasattr(orden, 'comprador') and getattr(orden.comprador, 'name', None):
            comprador_nombre = orden.comprador.name
        else:
            # Si no está cargada, realiza una consulta a la base de datos.
            comprador = Usuario.query.get(orden.comprador_id)
            comprador_nombre = comprador.name if comprador else 'N/A'

        # Obtiene el estado del viaje asociado a la orden, si existe.
        # Si la orden tiene un viaje asociado, se usa el estado del viaje.
        if hasattr(orden, 'viaje') and orden.viaje:
            estado_viaje = orden.viaje.estado
        else:
            # De lo contrario, se usa el estado de la propia orden.
            estado_viaje = orden.estado

        # Agrega un diccionario con los datos estructurados de la venta a la lista.
        data.append({
            'fecha_hora': orden.creado_en,  # Objeto datetime para ordenamiento.
            'producto': producto_map.get(item.producto_id, 'Producto no encontrado'), # Busca el nombre del producto.
            'cantidad': item.cantidad,
            'precio_unitario': item.precio_unitario,
            'total': item.cantidad * item.precio_unitario,
            'comprador_id': orden.comprador_id,
            'comprador_nombre': comprador_nombre,
            'estado': estado_viaje
        })

    # Si no se procesaron datos, devuelve una lista vacía para evitar errores.
    if not data:
        return []

    # Convierte la lista de diccionarios en un DataFrame de pandas para facilitar la manipulación.
    df = pd.DataFrame(data)

    # Ordena los datos por fecha y hora en orden descendente (los más recientes primero).
    df = df.sort_values(by='fecha_hora', ascending=False)

    # Crea una nueva columna con la fecha y hora formateadas como texto para su visualización.
    df['fecha_hora_str'] = df['fecha_hora'].dt.strftime('%Y-%m-%d %H:%M:%S')

    # Convierte el DataFrame de nuevo a una lista de diccionarios para ser usada en la plantilla.
    return df.to_dict(orient='records')
