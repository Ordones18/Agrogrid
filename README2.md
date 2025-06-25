# AgroGrid - Mapeo Integral del Proyecto

## 1. Propósito General

**AgroGrid** es una plataforma web diseñada para optimizar la cadena de suministro agrícola en Ecuador, conectando a **agricultores**, **compradores** y **transportistas**. El sistema facilita la comercialización de productos, provee análisis de datos en tiempo real y optimiza la logística de transporte para mejorar la eficiencia y la toma de decisiones de todos los actores involucrados.

### Tecnologías Clave

- **Backend**: Python, Flask, SQLAlchemy
- **Frontend**: HTML, CSS, JavaScript (Vanilla)
- **Análisis de Datos**: NumPy, Pandas
- **Bases de Datos**: SQLite (desarrollo), PostgreSQL (producción)
- **Optimización de Rutas**: NetworkX
- **Inteligencia Artificial**: DeepSeek (para el chatbot Gridi)

---

## 2. Estructura de Carpetas y Archivos

La estructura del proyecto es modular para facilitar su mantenimiento y escalabilidad.

```
Agrogrid/
|-- app/                           # Directorio principal de la aplicación
|   |-- __init__.py               # Inicializa la aplicación Flask y sus extensiones
|   |-- models.py                 # Define los modelos de la base de datos con SQLAlchemy
|   |-- routes.py                 # Contiene todas las rutas y endpoints de la API
|   |-- analytics.py              # Lógica para análisis de datos (ventas, compras)
|   |-- grafo_transporte.py       # Algoritmos de grafos para optimización de rutas
|   |-- chatbot_knowledge.py      # Base de conocimiento local para el chatbot
|   |-- chatbot_prompts.py        # Configuración y prompts para el modelo de IA
|   |-- utils/                    # Módulos de utilidad (ej. recomendador)
|   |-- static/                   # Archivos estáticos (CSS, JS, imágenes)
|   |-- templates/                # Plantillas HTML (Jinja2)
|       |-- agricultor/           # Vistas para el panel del agricultor
|       |-- comprador/            # Vistas para el panel del comprador
|       |-- transportista/        # Vistas para el panel del transportista
|       |-- admin/                # Vistas para el panel de administración
|-- migrations/                   # Scripts de migración de la base de datos (Alembic)
|-- geojson/                      # Archivos GeoJSON para mapas y rutas
|-- instance/                     # Archivos de instancia (ej. BBDD SQLite)
|-- tests/                        # Pruebas unitarias y de integración
|-- config.py                     # Configuraciones de la aplicación
|-- requirements.txt              # Dependencias de Python
|-- run.py                        # Punto de entrada para ejecutar la aplicación
|-- .env                          # Archivo para variables de entorno
```

---

## 3. Roles de Usuario y Paneles

AgroGrid define cuatro roles principales, cada uno con un panel personalizado que ofrece herramientas y datos específicos para sus necesidades.

### a. Agricultor
- **Objetivo**: Vender sus cosechas de forma directa y eficiente.
- **Panel del Agricultor**:
  - **Gestión de Productos**: Publicar, editar y eliminar productos.
  - **Visualización de Ventas**: Dashboard con análisis de ventas totales, por producto y por período (semanal, mensual, anual) usando **NumPy** y **Pandas**.
  - **Gestión de Órdenes**: Ver y gestionar los pedidos recibidos.

### b. Comprador
- **Objetivo**: Encontrar y adquirir productos agrícolas de calidad al mejor precio.
- **Panel del Comprador**:
  - **Marketplace**: Explorar el catálogo de productos con filtros avanzados.
  - **Visualización de Compras**: Dashboard con análisis de compras totales y productos más comprados.
  - **Gestión de Órdenes**: Realizar seguimiento de sus pedidos.
  - **Recomendaciones**: Recibir sugerencias de productos basadas en su historial.

### c. Transportista
- **Objetivo**: Ofrecer servicios de logística y optimizar sus rutas de entrega.
- **Panel del Transportista**:
  - **Gestión de Viajes**: Aceptar y gestionar solicitudes de transporte.
  - **Optimización de Rutas**: Visualizar la ruta más eficiente para las entregas usando **NetworkX** y datos geoespaciales.
  - **Historial de Entregas**: Rastrear los viajes completados y las ganancias.

---

## 4. Instalación y Puesta en Marcha

Sigue estos pasos para configurar el entorno de desarrollo local.

1. **Clonar el Repositorio**
   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd Agrogrid
   ```

2. **Crear y Activar un Entorno Virtual**
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Linux/macOS
   venv\Scripts\activate    # En Windows
   ```

3. **Instalar Dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar Variables de Entorno**
   - Renombra el archivo `.env.example` a `.env`.
   - Añade tus claves de API (como `DEEPSEEK_API_KEY`) y otras configuraciones necesarias.

5. **Aplicar Migraciones de la Base de Datos**
   ```bash
   flask db upgrade
   ```

6. **Ejecutar la Aplicación**
   ```bash
   python run.py
   ```

---

## 5. Módulos Clave y Funcionalidades

### a. Análisis de Datos (`analytics.py`)
Este módulo utiliza **NumPy** para cálculos numéricos eficientes y **Pandas** para la manipulación de datos. Proporciona funciones para agregar ventas y compras, agruparlas por períodos y generar los datos necesarios para los dashboards de los usuarios.

### b. Chatbot con IA (`chatbot_prompts.py` y `chatbot_knowledge.py`)
- **Gridi**, el chatbot de soporte, utiliza un sistema de dos capas:
  1. **Base de Conocimiento Local**: Responde instantáneamente a preguntas frecuentes definidas en `chatbot_knowledge.py`.
  2. **Modelo de IA (DeepSeek)**: Si la pregunta no se encuentra localmente, se envía al modelo de lenguaje configurado en `chatbot_prompts.py` para obtener una respuesta inteligente.

### c. Optimización de Rutas (`grafo_transporte.py`)
Utiliza la librería **NetworkX** para modelar la red de transporte de Ecuador como un grafo. Calcula las rutas más cortas y eficientes entre cantones, optimizando la logística para los transportistas.

---


