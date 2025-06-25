# recomendador.py
# Lógica de recomendación de productos para compradores
import pandas as pd
from collections import Counter
from app.models import Orden, Producto, Usuario, OrdenItem
from sqlalchemy.orm import joinedload
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def recomendar_productos_para_usuario(user_id, max_n=10):
    """
    Sistema híbrido: KNN colaborativo + basado en contenido.
    1. Si el usuario tiene historial suficiente, usa KNN colaborativo.
    2. Si no, recomienda por contenido (tipo, región, categoría).
    """
    # --- 1. Preparar datos de compras ---
    usuarios = Usuario.query.filter_by(user_type='comprador').all()
    productos = Producto.query.filter(Producto.cantidad > 0).all()
    productos_dict = {p.id: p for p in productos}
    producto_ids = list(productos_dict.keys())
    user_ids = [u.id for u in usuarios]

    # Matriz usuario-producto (compras)
    data = []
    for u in usuarios:
        ordenes = Orden.query.filter_by(comprador_id=u.id).options(joinedload(Orden.items)).all()
        compras = Counter()
        for orden in ordenes:
            for item in orden.items:
                compras[item.producto_id] += item.cantidad
        row = [compras[pid] for pid in producto_ids]
        data.append(row)
    df = pd.DataFrame(data, index=user_ids, columns=producto_ids)

    # --- 2. Recomendar por KNN colaborativo ---
    if user_id in df.index and df.loc[user_id].sum() > 0:
        # KNN sobre usuarios
        knn = NearestNeighbors(n_neighbors=min(6, len(df)), metric='cosine')
        knn.fit(df)
        user_vec = df.loc[[user_id]]
        dists, idxs = knn.kneighbors(user_vec, return_distance=True)
        vecinos = [df.index[i] for i in idxs[0] if df.index[i] != user_id]
        # Sumar compras de vecinos, restar propias
        scores = Counter()
        for v in vecinos:
            for pid, val in df.loc[v].items():
                if val > 0 and df.loc[user_id, pid] == 0:
                    scores[pid] += val
        # Si hay recomendaciones, devolverlas
        top_ids = [pid for pid, _ in scores.most_common(max_n)]
        recomendados = [productos_dict[pid] for pid in top_ids if pid in productos_dict]
        if len(recomendados) >= max_n//2:
            return recomendados[:max_n]
    # --- 3. Si no hay historial o pocas compras, recomendar por contenido ---
    # Buscar productos que sean similares a los que ya compró
    ordenes = Orden.query.filter_by(comprador_id=user_id).options(joinedload(Orden.items)).all()
    comprados = set()
    for orden in ordenes:
        for item in orden.items:
            comprados.add(item.producto_id)
    if comprados:
        # Usar tipo y región para similitud
        comprados_prods = [productos_dict[pid] for pid in comprados if pid in productos_dict]
        if not comprados_prods:
            return []
        tipos = set(p.tipo for p in comprados_prods)
        regiones = set(p.region for p in comprados_prods)
        # Score por coincidencia de tipo y región
        scores = []
        for p in productos:
            if p.id in comprados:
                continue
            score = 0
            if p.tipo in tipos:
                score += 2
            if p.region in regiones:
                score += 1
            scores.append((p, score))
        scores.sort(key=lambda x: -x[1])
        recomendados = [p for p, s in scores if s > 0][:max_n]
        if recomendados:
            return recomendados
    # --- 4. Fallback: productos más populares (por ventas globales) ---
    orden_items = OrdenItem.query.all()
    ventas = Counter()
    for item in orden_items:
        ventas[item.producto_id] += item.cantidad
    top_ids = [pid for pid, _ in ventas.most_common(max_n)]
    return [productos_dict[pid] for pid in top_ids if pid in productos_dict]
