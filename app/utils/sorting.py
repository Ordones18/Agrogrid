"""
Módulo de utilidades para comparar Quick Sort y Merge Sort en Agrogrid.
Incluye funciones de ordenamiento y benchmarking.

¿Cómo se usan estas funciones?
------------------------------
- En routes.py existe una función llamada 'sort_products' que recibe la lista de productos y el algoritmo elegido.
- Según el criterio de ordenamiento, se define la función key y se llama a quicksort() o mergesort() importados de este módulo.
- El resultado es una lista de productos ordenados que luego se muestra en la interfaz.

"""
import time

def quicksort(arr, key=None):
    """
    Ordena una lista usando el algoritmo QuickSort.
    Permite ordenar cualquier tipo de objeto usando una función key.
    - arr: lista a ordenar
    - key: función opcional para extraer el valor a comparar
    """
    if len(arr) <= 1:
        # Caso base: listas vacías o de un elemento ya están ordenadas
        return arr
    if key is None:
        key = lambda x: x  # Si no se especifica, usar el valor directo
    pivot = arr[len(arr) // 2]  # Selecciona el elemento pivote
    pivot_key = key(pivot)
    # Divide la lista en menores, iguales y mayores al pivote
    left = [x for x in arr if key(x) < pivot_key]
    middle = [x for x in arr if key(x) == pivot_key]
    right = [x for x in arr if key(x) > pivot_key]
    # Aplica recursividad y concatena los resultados
    return quicksort(left, key) + middle + quicksort(right, key)


def mergesort(arr, key=None):
    """
    Ordena una lista usando el algoritmo MergeSort.
    Permite ordenar cualquier tipo de objeto usando una función key.
    - arr: lista a ordenar
    - key: función opcional para extraer el valor a comparar
    """
    if len(arr) <= 1:
        # Caso base: listas vacías o de un elemento ya están ordenadas
        return arr
    if key is None:
        key = lambda x: x  # Si no se especifica, usar el valor directo
    mid = len(arr) // 2
    # Divide la lista en dos mitades y ordena cada una recursivamente
    left = mergesort(arr[:mid], key)
    right = mergesort(arr[mid:], key)
    # Mezcla las dos mitades ordenadas
    return merge(left, right, key)


def merge(left, right, key):
    """
    Función auxiliar para MergeSort.
    Mezcla dos listas ordenadas en una sola lista ordenada.
    - left: primera mitad ordenada
    - right: segunda mitad ordenada
    - key: función para extraer el valor a comparar
    """
    result = []
    i = j = 0
    # Recorre ambas listas y agrega el menor elemento de cada una
    while i < len(left) and j < len(right):
        if key(left[i]) < key(right[j]):
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    # Agrega los elementos restantes (si los hay)
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def benchmark_sorts(arr, tipo_dato='numeros'):
    """
    Ejecuta y compara el rendimiento de QuickSort y MergeSort sobre la misma lista.
    Parámetros:
        arr: lista a ordenar
        tipo_dato: descripción del tipo de datos ('numeros', 'productos', etc.)
    Retorna:
        Diccionario con tiempos y resultados de ambos algoritmos.
    """
    arr1 = list(arr)  # Copia para QuickSort
    arr2 = list(arr)  # Copia para MergeSort
    t0 = time.time()
    quick = quicksort(arr1)
    t1 = time.time()
    merge = mergesort(arr2)
    t2 = time.time()
    is_sorted = (arr == sorted(arr))
    return {
        'tipo': tipo_dato,
        'n': len(arr),
        'ya_ordenada': is_sorted,
        'quicksort': {'result': quick, 'time': t1-t0},
        'mergesort': {'result': merge, 'time': t2-t1}
    }


