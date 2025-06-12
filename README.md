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
```
python
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

# Agrogrid

Agrogrid es una plataforma web para la gestión y optimización de la cadena de suministro agrícola, conectando agricultores, compradores y transportistas, y facilitando la administración de productos, órdenes y rutas de transporte entre cantones.

## Estructura del Proyecto

```
Agrogrid/
├── app/
│   ├── __init__.py
│   ├── analytics_historial.py
│   ├── analytics.py
│   ├── controllers.py
│   ├── grafo_transporte.py
│   ├── models.py
│   ├── routes.py
│   ├── taxonomia.py
│   ├── ubicacion.py
│   ├── utils.py
│   ├── static/
│   │   ├── css/
│   │   ├── images/
│   │   ├── js/
│   │   └── uploads/
│   └── templates/
│       ├── about.html
│       ├── ...
│       ├── agricultor/
│       ├── comprador/
│       ├── email/
│       ├── partials/
│       └── transportista/
├── config.py
├── crear_tablas_sqlalchemy.py
├── grafo_cantonal_geodesico.json
├── grafo_cantonal_vecinos.json
├── poblar_coordenadas_cantones.py
├── poblar_grafo_ors.py
├── poblar_grafo_vecinos.py
├── run.py
├── testingdb.py
├── ver_bd_estructura.py
├── ver_cantones_latlon.py
├── geojson/
│   └── cantons.geojson
├── instance/
│   └── agrogrid.db
├── migrations/
│   ├── alembic.ini
│   ├── env.py
│   ├── README
│   ├── script.py.mako
│   ├── versions/
│   │   └── *.py
├── scripts/
│   ├── eliminar_viajes_por_definir.py
│   └── poblar_viajes.py
└── README.md
```

## Descripción de Carpetas y Archivos Principales

- **app/**: Lógica principal de la aplicación, modelos, controladores, rutas, utilidades y recursos estáticos/plantillas.
  - **static/**: Archivos estáticos (CSS, JS, imágenes, uploads de usuarios).
  - **templates/**: Plantillas HTML para la interfaz web.
- **config.py**: Configuración general de la aplicación.
- **geojson/**: Archivos geográficos para visualización y análisis espacial.
- **instance/**: Base de datos local (no versionar en producción).
- **migrations/**: Migraciones de base de datos gestionadas con Alembic.
- **scripts/**: Scripts para poblar datos y tareas administrativas.
- **grafo_cantonal_*.json**: Datos de grafos geográficos para rutas y análisis de transporte.
- **run.py**: Punto de entrada principal de la aplicación.
- **README.md**: Documentación del proyecto.

## Dependencias principales
- Python 3.x
- Flask
- SQLAlchemy
- Alembic
- Numpy
- Pandas


# =============================
# INSTRUCCIONES DE INSTALACIÓN Y USO DE DATOS ESTRUCTURALES
# =============================

## Instalación y carga de datos estructurales

1. **Clona el repositorio y entra al directorio:**
   ```bash
   git clone <url-del-repo>
   cd Agrogrid
   ```

2. **Crea y activa un entorno virtual (opcional pero recomendado):**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # En Windows
   source .venv/bin/activate  # En Linux/Mac
   ```

3. **Instala las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Crea la estructura de la base de datos:**
   Ejecuta las migraciones para crear todas las tablas necesarias:
   ```bash
   flask db upgrade
   ```
   O si tienes un script para crear tablas:
   ```bash
   python crear_tablas_sqlalchemy.py
   ```

5. **Carga los datos estructurales (ubicaciones y taxonomía):**
   Si ya tienes los archivos JSON exportados (`export_region.json`, `export_provincia.json`, `export_canton.json`, `export_categoria.json`, `export_subcategoria.json`), ejecuta:
   ```bash
   python scripts/importar_tablas_json.py
   ```
   Esto poblará las tablas:
   - Region
   - Provincia
   - Canton
   - Categoria
   - Subcategoria

   Si necesitas generar estos archivos desde una base de datos existente, ejecuta:
   ```bash
   python scripts/exportar_tablas_json.py
   ```

6. **Tablas adicionales:**
   Las tablas de usuarios, productos, carritos, órdenes, viajes y favoritos se crearán vacías. Estas se llenarán a medida que los usuarios interactúen con la aplicación.

   - Usuario
   - Producto
   - Carrito
   - DetalleCarrito
   - Orden
   - OrdenItem
   - Viaje
   - favoritos

   Si necesitas poblar datos de ejemplo para pruebas, puedes crear scripts adicionales o poblar manualmente desde la app.

7. **Ejecuta la aplicación:**
   ```bash
   python run.py
   ```

---
