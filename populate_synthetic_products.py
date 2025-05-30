import os
from app import app, db
from app.models import Producto

# Datos sintéticos de productos ecuatorianos
productos_sinteticos = [
    {
        'nombre': 'Banano',
        'tipo': 'Fruta',
        'region': 'Costa',
        'provincia': 'El Oro',
        'precio': 18.50,
        'unidad': 'Caja',
        'descripcion': 'Banano de exportación, calidad premium.',
        'cantidad': 100,
        'vistas': 25
    },
    {
        'nombre': 'Papa',
        'tipo': 'Tubérculo',
        'region': 'Sierra',
        'provincia': 'Tungurahua',
        'precio': 22.00,
        'unidad': 'Quintal',
        'descripcion': 'Papa chola, ideal para consumo y fritura.',
        'cantidad': 50,
        'vistas': 40
    },
    {
        'nombre': 'Cacao',
        'tipo': 'Grano',
        'region': 'Costa',
        'provincia': 'Manabí',
        'precio': 120.00,
        'unidad': 'Quintal',
        'descripcion': 'Cacao nacional fino de aroma.',
        'cantidad': 20,
        'vistas': 15
    },
    {
        'nombre': 'Tomate de árbol',
        'tipo': 'Fruta',
        'region': 'Sierra',
        'provincia': 'Imbabura',
        'precio': 0.80,
        'unidad': 'Kg',
        'descripcion': 'Tomate de árbol fresco, ideal para jugos.',
        'cantidad': 200,
        'vistas': 10
    },
    {
        'nombre': 'Yuca',
        'tipo': 'Tubérculo',
        'region': 'Amazonía',
        'provincia': 'Napo',
        'precio': 0.60,
        'unidad': 'Kg',
        'descripcion': 'Yuca tierna, cosecha reciente.',
        'cantidad': 150,
        'vistas': 8
    },
    {
        'nombre': 'Maíz',
        'tipo': 'Grano',
        'region': 'Costa',
        'provincia': 'Guayas',
        'precio': 16.00,
        'unidad': 'Quintal',
        'descripcion': 'Maíz duro seco, excelente para balanceados.',
        'cantidad': 60,
        'vistas': 12
    },
    {
        'nombre': 'Naranjilla',
        'tipo': 'Fruta',
        'region': 'Amazonía',
        'provincia': 'Morona Santiago',
        'precio': 1.20,
        'unidad': 'Kg',
        'descripcion': 'Naranjilla fresca, ideal para jugos.',
        'cantidad': 80,
        'vistas': 5
    },
    {
        'nombre': 'Zanahoria',
        'tipo': 'Hortaliza',
        'region': 'Sierra',
        'provincia': 'Bolívar',
        'precio': 0.90,
        'unidad': 'Kg',
        'descripcion': 'Zanahoria orgánica, sin pesticidas.',
        'cantidad': 120,
        'vistas': 18
    },
    {
        'nombre': 'Cebolla paiteña',
        'tipo': 'Hortaliza',
        'region': 'Sierra',
        'provincia': 'Carchi',
        'precio': 1.10,
        'unidad': 'Kg',
        'descripcion': 'Cebolla paiteña fresca, ideal para ensaladas.',
        'cantidad': 90,
        'vistas': 7
    },
    {
        'nombre': 'Mora',
        'tipo': 'Fruta',
        'region': 'Sierra',
        'provincia': 'Pichincha',
        'precio': 2.50,
        'unidad': 'Kg',
        'descripcion': 'Mora de castilla, dulce y jugosa.',
        'cantidad': 60,
        'vistas': 20
    },
]

usuario_id = 4  # ID del agricultor existente

with app.app_context():
    for prod in productos_sinteticos:
        producto = Producto(
            nombre=prod['nombre'],
            tipo=prod['tipo'],
            region=prod['region'],
            provincia=prod['provincia'],
            inicial_nombre=prod['nombre'][0].upper(),
            imagen_url=None,
            usuario_id=usuario_id,
            precio=prod['precio'],
            unidad=prod['unidad'],
            descripcion=prod['descripcion'],
            cantidad=prod['cantidad'],
            vistas=prod['vistas']
        )
        db.session.add(producto)
    db.session.commit()
    print(f"{len(productos_sinteticos)} productos sintéticos agregados para el usuario agricultor con ID {usuario_id}.") 