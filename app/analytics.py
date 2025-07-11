import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta

def numpy_agrupa_entregas_por_periodo(fechas_entrega, modo='semana', n=12):
    """
    Agrupa y cuenta fechas de entrega usando numpy por semana, mes o año.
    - fechas_entrega: lista de datetime
    - modo: 'semana', 'mes' o 'año'
    - n: cantidad de periodos a mostrar (por defecto 12)
    Devuelve:
      etiquetas: lista de str (ej: ['2025-23', ...] para semanas)
      cantidades: lista de int (ej: [3, 7, ...])
    """
    import numpy as np
    from datetime import datetime
    fechas = np.array([f for f in fechas_entrega if f])
    if len(fechas) == 0:
        return [], []
    if modo == 'semana':
        periodos = np.array([f"{f.year}-W{f.isocalendar()[1]:02d}" for f in fechas])
    elif modo == 'mes':
        periodos = np.array([f.strftime('%Y-%m') for f in fechas])
    elif modo == 'año':
        periodos = np.array([str(f.year) for f in fechas])
    else:
        raise ValueError('Modo debe ser semana, mes o año')
    unique_periods, counts = np.unique(periodos, return_counts=True)
    # Ordenar periodos por fecha real
    if modo == 'semana':
        sort_keys = np.array([int(p[:4])*100 + int(p[-2:]) for p in unique_periods])
    elif modo == 'mes':
        sort_keys = np.array([int(p[:4])*100 + int(p[-2:]) for p in unique_periods])
    else:
        sort_keys = np.array([int(p) for p in unique_periods])
    idx = np.argsort(sort_keys)
    unique_periods = unique_periods[idx]
    counts = counts[idx]
    etiquetas = unique_periods[-n:].tolist()
    cantidades = counts[-n:].tolist()
    return etiquetas, cantidades

def numpy_agrupa_ganancias_por_periodo(fechas_y_montos, modo='semana', n=12):
    """
    Agrupa y suma ganancias usando numpy por semana, mes o año.
    - fechas_y_montos: lista de tuplas (fecha_entrega, monto)
    - modo: 'semana', 'mes' o 'año'
    - n: cantidad de periodos a mostrar (por defecto 12)
    Devuelve:
      etiquetas: lista de str (ej: ['2025-23', ...] para semanas)
      montos: lista de float (ej: [120.0, 300.5, ...])
    """
    import numpy as np
    fechas = np.array([f for f, m in fechas_y_montos if f and m is not None])
    montos = np.array([m for f, m in fechas_y_montos if f and m is not None])
    if len(fechas) == 0:
        return [], []
    if modo == 'semana':
        periodos = np.array([f"{f.year}-W{f.isocalendar()[1]:02d}" for f in fechas])
    elif modo == 'mes':
        periodos = np.array([f.strftime('%Y-%m') for f in fechas])
    elif modo == 'año':
        periodos = np.array([str(f.year) for f in fechas])
    else:
        raise ValueError('Modo debe ser semana, mes o año')
    unique_periods = np.unique(periodos)
    sumas = np.array([montos[periodos == p].sum() for p in unique_periods])
    # Ordenar periodos por fecha real
    if modo == 'semana':
        sort_keys = np.array([int(p[:4])*100 + int(p[-2:]) for p in unique_periods])
    elif modo == 'mes':
        sort_keys = np.array([int(p[:4])*100 + int(p[-2:]) for p in unique_periods])
    else:
        sort_keys = np.array([int(p) for p in unique_periods])
    idx = np.argsort(sort_keys)
    unique_periods = unique_periods[idx]
    sumas = sumas[idx]
    etiquetas = unique_periods[-n:].tolist()
    montos = sumas[-n:].tolist()
    return etiquetas, montos

def generar_barplot_envios_entregados(fechas_entrega, static_path='app/static/barplot_envios.png'):
    """
    Genera un gráfico de barras con la cantidad de pedidos entregados por semana, mes, año y total.
    - fechas_entrega: lista de datetime (fechas de entrega de los viajes entregados)
    - static_path: ruta donde guardar la imagen
    Devuelve la url relativa para Flask (ej: 'barplot_envios.png')
    """
    now = datetime.utcnow()
    fechas = [f for f in fechas_entrega if f]
    semana = sum(1 for f in fechas if f >= now - timedelta(days=7))
    mes = sum(1 for f in fechas if f >= now - timedelta(days=30))
    anio = sum(1 for f in fechas if f >= now - timedelta(days=365))
    total = len(fechas)
    valores = [semana, mes, anio, total]
    etiquetas = ['Semana', 'Mes', 'Año', 'Total']

    plt.figure(figsize=(6,3.2))
    bars = plt.bar(etiquetas, valores, color=['#43b97f','#229e60','#388e3c','#b0e5c7'])
    plt.title('Pedidos Entregados')
    plt.ylabel('Cantidad')
    plt.ylim(0, max(valores+[1]))
    for bar in bars:
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height()+0.1, str(int(bar.get_height())), ha='center', va='bottom', fontsize=11)
    plt.tight_layout()
    plt.savefig(static_path, bbox_inches='tight', transparent=False)
    plt.close()
    # Devuelve solo el nombre de archivo para url_for('static', ...)
    return os.path.basename(static_path)

import pandas as pd

def calcular_compras_agregadas(orden_items, producto_map):
    """
    Recibe una lista de tuplas (OrdenItem, Orden) y un dict producto_map {producto_id: nombre}.
    Devuelve un dict con total gastado, productos más comprados (por cantidad y por gasto), y compras por periodo (semana, mes, año).
    """
    fechas = []
    totales = []
    productos_nombres = []
    cantidades = []

    for item, orden in orden_items:
        fechas.append(orden.creado_en)
        totales.append(item.cantidad * item.precio_unitario)
        productos_nombres.append(producto_map.get(item.producto_id, item.producto_nombre or 'Producto eliminado'))
        cantidades.append(item.cantidad)

    if not fechas:
        return {
            'total_gastado': 0,
            'por_producto_gasto': {},
            'por_producto_cantidad': {},
            'por_semana': {},
            'por_mes': {},
            'por_anio': {},
            'producto_top_gasto': None,
            'producto_top_cantidad': None
        }

    fechas_np = np.array(fechas)
    totales_np = np.array(totales)
    productos_np = np.array(productos_nombres)
    cantidades_np = np.array(cantidades)

    total_gastado = float(np.sum(totales_np))
    productos_unicos = np.unique(productos_np)
    por_producto_gasto = {
        prod: float(np.sum(totales_np[productos_np == prod]))
        for prod in productos_unicos
    }
    por_producto_cantidad = {
        prod: int(np.sum(cantidades_np[productos_np == prod]))
        for prod in productos_unicos
    }
    producto_top_gasto = max(por_producto_gasto, key=por_producto_gasto.get) if por_producto_gasto else None
    producto_top_cantidad = max(por_producto_cantidad, key=por_producto_cantidad.get) if por_producto_cantidad else None

    fechas_pd = pd.to_datetime(fechas_np)
    df = pd.DataFrame({
        'fecha': fechas_pd,
        'total': totales_np
    })
    df['anio'] = df['fecha'].dt.year
    df['mes'] = df['fecha'].dt.strftime('%Y-%m')
    df['semana'] = df['fecha'].dt.strftime('%Y-%U')
    df['dia'] = df['fecha'].dt.strftime('%Y-%m-%d')

    por_anio = df.groupby('anio')['total'].sum().to_dict()
    por_mes = df.groupby('mes')['total'].sum().to_dict()
    por_semana = df.groupby('semana')['total'].sum().to_dict()
    por_dia = df.groupby('dia')['total'].sum().to_dict()

    por_anio = {str(k): float(v) for k, v in por_anio.items()}
    por_mes = {str(k): float(v) for k, v in por_mes.items()}
    por_semana = {str(k): float(v) for k, v in por_semana.items()}
    por_dia = {str(k): float(v) for k, v in por_dia.items()}

    return {
        'total_gastado': total_gastado,
        'por_producto_gasto': por_producto_gasto,
        'por_producto_cantidad': por_producto_cantidad,
        'por_semana': por_semana,
        'por_mes': por_mes,
        'por_anio': por_anio,
        'por_dia': por_dia,
        'producto_top_gasto': producto_top_gasto,
        'producto_top_cantidad': producto_top_cantidad
    }


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
