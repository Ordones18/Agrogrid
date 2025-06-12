import pandas as pd

def preparar_historial_ventas(orden_items, producto_map):
    """
    Recibe una lista de tuplas (OrdenItem, Orden) y un dict producto_map {producto_id: nombre}.
    Devuelve una lista de dicts ordenada por fecha/hora descendente, con los datos listos para mostrar en una tabla.
    """
    data = []
    from app.models import Usuario
    for item, orden in orden_items:
        # Obtener el nombre del comprador de la relación o con consulta directa
        comprador_nombre = None
        if hasattr(orden, 'comprador') and getattr(orden.comprador, 'name', None):
            comprador_nombre = orden.comprador.name
        else:
            comprador = Usuario.query.get(orden.comprador_id)
            comprador_nombre = comprador.name if comprador else None
        # Obtener estado real del viaje asociado a la orden
        estado_viaje = None
        if hasattr(orden, 'viaje') and orden.viaje:
            estado_viaje = orden.viaje.estado
        else:
            estado_viaje = orden.estado
        data.append({
            'fecha_hora': orden.creado_en,  # datetime real
            'producto': producto_map[item.producto_id],
            'cantidad': item.cantidad,
            'precio_unitario': item.precio_unitario,
            'total': item.cantidad * item.precio_unitario,
            'comprador_id': orden.comprador_id,
            'comprador_nombre': comprador_nombre,
            'estado': estado_viaje
        })
    if not data:
        return []
    df = pd.DataFrame(data)
    df = df.sort_values(by='fecha_hora', ascending=False)
    # Formatea fecha/hora para la tabla
    df['fecha_hora_str'] = df['fecha_hora'].dt.strftime('%Y-%m-%d %H:%M:%S')
    return df.to_dict(orient='records')
