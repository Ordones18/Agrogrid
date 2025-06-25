# Uso de QuickSort y MergeSort en AgroGrid

Este módulo (`sorting.py`) implementa los algoritmos de ordenamiento QuickSort y MergeSort para ordenar listas de productos y otros datos en AgroGrid.

## Implementación
- **`quicksort(arr, key=None)`**: Ordena una lista usando el algoritmo QuickSort. Permite pasar una función `key` para ordenar por un atributo específico.
- **`mergesort(arr, key=None)`**: Ordena una lista usando el algoritmo MergeSort. También acepta una función `key` para orden personalizado.
- **`benchmark_sorts(arr, tipo_dato)`**: Permite comparar el rendimiento de ambos algoritmos sobre la misma lista.

## Uso en la App
En la vista de productos (`productos.html`), los usuarios pueden elegir el algoritmo de ordenamiento desde el panel de filtros. El backend recibe la selección y utiliza el método correspondiente:

- Si el usuario selecciona "QuickSort", se llama a la función `quicksort` de `sorting.py`.
- Si el usuario selecciona "MergeSort", se llama a la función `mergesort` de `sorting.py`.

Esto se gestiona en la función `sort_products` de `routes.py`:

```python
from app.utils.sorting import quicksort, mergesort
...
if sort_algo == 'mergesort':
    arr = mergesort(arr, key=key_fn)
else:
    arr = quicksort(arr, key=key_fn)
```

De esta manera, los productos pueden ordenarse por ventas, vistas o recientes usando el algoritmo seleccionado por el usuario.

## Ejemplo de uso
```python
from app.utils.sorting import quicksort, mergesort
productos_ordenados = quicksort(productos, key=lambda p: p.precio)
# o
productos_ordenados = mergesort(productos, key=lambda p: p.nombre)
```

## Notas
- Ambos algoritmos funcionan con cualquier lista de objetos, siempre que se proporcione una función `key` adecuada.
- El rendimiento de cada algoritmo puede variar según el tamaño y tipo de datos; por eso se incluye la función de benchmarking.

------------------------------------------------------------------------------------------------------------------


# Algoritmo Híbrido de Recomendación de Productos (recomendador.py)

Este módulo implementa un sistema de recomendación híbrido para compradores en AgroGrid, combinando filtrado colaborativo (KNN) y recomendaciones basadas en contenido.

## ¿Cómo funciona?

1. **Filtrado colaborativo (KNN):**
   - Si el usuario tiene historial de compras suficiente, se buscan usuarios "similares" (vecinos) usando KNN sobre una matriz usuario-producto.
   - Se recomiendan productos que han comprado los vecinos pero que el usuario aún no ha comprado.

2. **Basado en contenido:**
   - Si el usuario tiene poco o ningún historial, se recomiendan productos similares a los que ya compró, usando atributos como tipo y región.
   - Se asigna mayor peso a coincidencias de tipo y menor a región.

3. **Fallback (popularidad):**
   - Si no hay historial ni productos similares, se recomiendan los productos más vendidos globalmente.

## Detalles técnicos
- **Librerías:**
  - `pandas`, `scikit-learn` (para la matriz y KNN)
  - `collections.Counter` (para agregados rápidos)
- **Modelos usados:** `Usuario`, `Orden`, `OrdenItem`, `Producto`.
- **Función principal:** `recomendar_productos_para_usuario(user_id, max_n=10)`
- **Personalización:** Puedes ajustar los pesos de tipo/región, el número de vecinos KNN, o agregar más atributos/productos al cálculo.

## Modificación y extensión
- Para mejorar el algoritmo, puedes:
  - Añadir más atributos al análisis de similitud (por ejemplo, subcategoría, precio).
  - Cambiar el número de vecinos en KNN (`n_neighbors`).
  - Integrar feedback del usuario (favoritos, clicks, etc.).
  - Optimizar la performance con caching si la base crece.

---

Para dudas o mejoras, edita `recomendador.py` y ajusta la función principal según tus necesidades.
