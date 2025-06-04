import numpy as np
import pandas as pd

def calcular_ventas_agregadas(orden_items, producto_map):
    """
    Recibe una lista de tuplas (OrdenItem, Orden) y un dict producto_map {producto_id: nombre}.
    Devuelve un dict con ventas totales, por producto y por periodo (semana, mes, año).
    """
    fechas = []
    totales = []
    productos_nombres = []
    cantidades = []

    for item, orden in orden_items:
        fechas.append(orden.creado_en)
        totales.append(item.cantidad * item.precio_unitario)
        productos_nombres.append(producto_map[item.producto_id])
        cantidades.append(item.cantidad)

    if not fechas:
        return {
            'total_general': 0,
            'por_producto': {},
            'por_semana': {},
            'por_mes': {},
            'por_anio': {}
        }

    fechas_np = np.array(fechas)
    totales_np = np.array(totales)
    productos_np = np.array(productos_nombres)

    total_general = float(np.sum(totales_np))
    productos_unicos = np.unique(productos_np)
    por_producto = {
        prod: float(np.sum(totales_np[productos_np == prod]))
        for prod in productos_unicos
    }

    fechas_pd = pd.to_datetime(fechas_np)
    df = pd.DataFrame({
        'fecha': fechas_pd,
        'total': totales_np
    })
    df['anio'] = df['fecha'].dt.year
    df['mes'] = df['fecha'].dt.strftime('%Y-%m')
    df['semana'] = df['fecha'].dt.strftime('%Y-%U')

    por_anio = df.groupby('anio')['total'].sum().to_dict()
    por_mes = df.groupby('mes')['total'].sum().to_dict()
    por_semana = df.groupby('semana')['total'].sum().to_dict()

    por_anio = {str(k): float(v) for k, v in por_anio.items()}
    por_mes = {str(k): float(v) for k, v in por_mes.items()}
    por_semana = {str(k): float(v) for k, v in por_semana.items()}

    return {
        'total_general': total_general,
        'por_producto': por_producto,
        'por_semana': por_semana,
        'por_mes': por_mes,
        'por_anio': por_anio
    }
