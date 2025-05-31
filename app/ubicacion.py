# ubicacion.py
# Árbol de clasificación de ubicación para Ecuador: Región > Provincia > Cantón
# Estructura y funciones para exponer la jerarquía al frontend y guardar en la base de datos

UBICACION_ECUADOR = {
    'Costa': {
        'Esmeraldas': ['Esmeraldas', 'Atacames', 'Quinindé', 'Muisne', 'Rioverde', 'San Lorenzo', 'Eloy Alfaro'],
        'Manabí': ['Portoviejo', 'Manta', 'Chone', 'Jipijapa', 'Montecristi', 'El Carmen', 'Rocafuerte', 'Sucre', 'Tosagua', 'Pedernales', 'Paján', 'Flavio Alfaro', 'Santa Ana', '24 de Mayo', 'Bolívar', 'Jama', 'Jaramijó', 'Olmedo', 'San Vicente'],
        'Guayas': ['Guayaquil', 'Daule', 'Samborondón', 'Durán', 'Milagro', 'Naranjal', 'Balao', 'Balzar', 'Colimes', 'El Empalme', 'El Triunfo', 'General Antonio Elizalde', 'Isidro Ayora', 'Lomas de Sargentillo', 'Marcelino Maridueña', 'Naranjito', 'Nobol', 'Palestina', 'Pedro Carbo', 'Playas', 'Salitre', 'San Jacinto de Yaguachi', 'Santa Lucía', 'Simón Bolívar'],
        'Santa Elena': ['Santa Elena', 'La Libertad', 'Salinas'],
        'El Oro': ['Machala', 'Santa Rosa', 'Pasaje', 'Huaquillas', 'Arenillas', 'Atahualpa', 'Balsas', 'Chilla', 'El Guabo', 'Las Lajas', 'Marcabelí', 'Piñas', 'Portovelo', 'Zaruma'],
        'Los Ríos': ['Babahoyo', 'Quevedo', 'Vinces', 'Baba', 'Buena Fe', 'Mocache', 'Montalvo', 'Palenque', 'Puebloviejo', 'Quinsaloma', 'Urdaneta', 'Valencia', 'Ventanas']
    },
    'Sierra': {
        'Carchi': ['Tulcán', 'Bolívar', 'Espejo', 'Mira', 'Montúfar', 'San Pedro de Huaca'],
        'Imbabura': ['Ibarra', 'Otavalo', 'Cotacachi', 'Antonio Ante', 'Pimampiro', 'San Miguel de Urcuquí'],
        'Pichincha': ['Quito', 'Cayambe', 'Mejía', 'Pedro Moncayo', 'Pedro Vicente Maldonado', 'Puerto Quito', 'Rumiñahui', 'San Miguel de los Bancos'],
        'Cotopaxi': ['Latacunga', 'La Maná', 'Pangua', 'Pujilí', 'Salcedo', 'Saquisilí', 'Sigchos'],
        'Tungurahua': ['Ambato', 'Baños', 'Cevallos', 'Mocha', 'Patate', 'Pelileo', 'Píllaro', 'Quero', 'Tisaleo'],
        'Bolívar': ['Guaranda', 'Chillanes', 'Chimbo', 'Echeandía', 'Las Naves', 'San Miguel'],
        'Chimborazo': ['Riobamba', 'Alausí', 'Chambo', 'Chunchi', 'Colta', 'Cumandá', 'Guamote', 'Guano', 'Pallatanga', 'Penipe'],
        'Cañar': ['Azogues', 'Biblián', 'Cañar', 'Déleg', 'El Tambo', 'La Troncal', 'Suscal'],
        'Azuay': ['Cuenca', 'Camilo Ponce Enríquez', 'Chordeleg', 'El Pan', 'Girón', 'Guachapala', 'Gualaceo', 'Nabón', 'Oña', 'Paute', 'Pucará', 'San Fernando', 'Santa Isabel', 'Sevilla de Oro', 'Sigsig'],
        'Loja': ['Loja', 'Calvas', 'Catamayo', 'Celica', 'Chaguarpamba', 'Espíndola', 'Gonzanamá', 'Macará', 'Olmedo', 'Paltas', 'Pindal', 'Puyango', 'Quilanga', 'Saraguro', 'Sozoranga', 'Zapotillo']
    },
    'Amazonía': {
        'Sucumbíos': ['Nueva Loja', 'Cascales', 'Cuyabeno', 'Gonzalo Pizarro', 'Lago Agrio', 'Putumayo', 'Shushufindi', 'Sucumbíos'],
        'Napo': ['Tena', 'Archidona', 'Carlos Julio Arosemena Tola', 'El Chaco', 'Quijos'],
        'Orellana': ['Francisco de Orellana', 'Aguarico', 'La Joya de los Sachas', 'Loreto'],
        'Pastaza': ['Puyo', 'Arajuno', 'Mera', 'Santa Clara'],
        'Morona Santiago': ['Macas', 'Gualaquiza', 'Huamboya', 'Limón Indanza', 'Logroño', 'Morona', 'Pablo Sexto', 'Palora', 'San Juan Bosco', 'Santiago', 'Sucúa', 'Taisha', 'Tiwintza'],
        'Zamora Chinchipe': ['Zamora', 'Centinela del Cóndor', 'Chinchipe', 'El Pangui', 'Nangaritza', 'Palanda', 'Paquisha', 'Yacuambi', 'Yantzaza']
    },
    'Galápagos': {
        'Galápagos': ['Puerto Ayora', 'Puerto Baquerizo Moreno', 'Puerto Villamil']
    }
}

def obtener_estructura_ubicacion():
    """
    Devuelve la estructura simple de ubicación para el frontend:
    {region: {provincia: [cantones]}}
    """
    return UBICACION_ECUADOR

# Si necesitas guardar la selección en la base de datos, puedes usar estos nombres de campo:
# region, provincia, canton
