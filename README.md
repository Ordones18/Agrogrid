# Agrogrid

## Uso de Numpy y Pandas en Agrogrid

En este proyecto utilizamos **Numpy** y **Pandas** para procesar y analizar los datos de ventas de manera eficiente y flexible. Ambas librerías son ampliamente usadas en ciencia de datos y análisis numérico en Python.

### ¿Por qué usamos Numpy y Pandas?
- **Numpy** permite realizar cálculos numéricos y agregaciones de manera muy rápida usando arreglos (arrays) en vez de listas tradicionales de Python.
- **Pandas** facilita la manipulación y agrupación de datos por fechas (por ejemplo, sumar ventas por semana, mes o año) usando DataFrames.

### Ejemplo de uso en Agrogrid
Cuando un agricultor consulta el detalle de sus ventas, el backend:
1. Extrae todas las ventas relacionadas a sus productos.
2. Usa Numpy para sumar totales y agrupar por producto.
3. Usa Pandas para agrupar las ventas por semana, mes y año, generando los datos que alimentan las gráficas del dashboard.

**Fragmento de código real:**
```python
import numpy as np
import pandas as pd

def calcular_ventas_agregadas(orden_items, producto_map):
    # ...
    fechas_np = np.array(fechas)
    totales_np = np.array(totales)
    productos_np = np.array(productos_nombres)
    total_general = float(np.sum(totales_np))
    por_producto = {
        prod: float(np.sum(totales_np[productos_np == prod]))
        for prod in np.unique(productos_np)
    }
    fechas_pd = pd.to_datetime(fechas_np)
    df = pd.DataFrame({'fecha': fechas_pd, 'total': totales_np})
    df['mes'] = df['fecha'].dt.strftime('%Y-%m')
    por_mes = df.groupby('mes')['total'].sum().to_dict()
    # ...
```

### Instalación
Si no tienes estas librerías, instálalas con:
```bash
pip install numpy pandas
```

**Nota:** Ambas librerías son dependencias necesarias para el correcto funcionamiento del análisis de ventas en Agrogrid.