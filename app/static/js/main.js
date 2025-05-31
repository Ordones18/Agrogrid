// Espera a que el contenido del DOM esté cargado antes de ejecutar el código
document.addEventListener('DOMContentLoaded', function() {
    // Selecciona el botón que abre/cierra el menú móvil
    const toggle = document.querySelector('.mobile-menu-toggle');
    // Selecciona la barra de navegación principal
    const nav = document.querySelector('.navigation');
    // Agrega un evento al botón para alternar la visibilidad del menú
    toggle.addEventListener('click', function() {
        // Alterna la clase 'active' en la navegación para mostrar u ocultar el menú en móviles
        nav.classList.toggle('active');
    });

    // ================= SCRIPT PARA PROVINCIAS DINÁMICAS =================
    // Provincias por región de Ecuador
    // Fuente: https://es.wikipedia.org/wiki/Organizaci%C3%B3n_territorial_del_Ecuador
    const provinciasPorRegion = {
        'Costa': [
            'Esmeraldas', 'Manabí', 'Guayas', 'Santa Elena', 'El Oro', 'Los Ríos'
        ],
        'Sierra': [
            'Carchi', 'Imbabura', 'Pichincha', 'Cotopaxi', 'Tungurahua', 'Bolívar', 'Chimborazo', 'Cañar', 'Azuay', 'Loja'
        ],
        'Amazonía': [
            'Sucumbíos', 'Napo', 'Orellana', 'Pastaza', 'Morona Santiago', 'Zamora Chinchipe'
        ],
        'Galápagos': [
            'Galápagos'
        ]
    };
    // Referencias a los selectores
    const regionSelect = document.getElementById('region');
    const provinciaSelect = document.getElementById('provincia');
    const cantonSelect = document.getElementById('canton');

    // Cantones principales por provincia (ejemplo, puedes expandir)
    const cantonesPorProvincia = {
        'Guayas': ['Guayaquil', 'Daule', 'Samborondón', 'Durán', 'Milagro', 'Naranjal'],
        'Pichincha': ['Quito', 'Cayambe', 'Mejía', 'Rumiñahui', 'Pedro Moncayo'],
        'Manabí': ['Portoviejo', 'Manta', 'Chone', 'Jipijapa', 'Montecristi'],
        'Azuay': ['Cuenca', 'Gualaceo', 'Paute', 'Girón'],
        'El Oro': ['Machala', 'Santa Rosa', 'Pasaje', 'Huaquillas'],
        'Loja': ['Loja', 'Catamayo', 'Macará', 'Saraguro'],
        'Tungurahua': ['Ambato', 'Baños', 'Pelileo'],
        'Imbabura': ['Ibarra', 'Otavalo', 'Cotacachi'],
        'Los Ríos': ['Babahoyo', 'Quevedo', 'Vinces'],
        'Chimborazo': ['Riobamba', 'Guano', 'Alausí'],
        'Cotopaxi': ['Latacunga', 'Salcedo', 'Pujilí'],
        'Esmeraldas': ['Esmeraldas', 'Atacames', 'Quinindé'],
        'Santa Elena': ['Santa Elena', 'La Libertad', 'Salinas'],
        'Carchi': ['Tulcán', 'Montúfar', 'Mira'],
        'Bolívar': ['Guaranda', 'Chillanes'],
        'Cañar': ['Azogues', 'Biblián'],
        'Morona Santiago': ['Macas', 'Gualaquiza'],
        'Napo': ['Tena', 'Archidona'],
        'Orellana': ['Francisco de Orellana'],
        'Pastaza': ['Puyo'],
        'Sucumbíos': ['Nueva Loja'],
        'Zamora Chinchipe': ['Zamora', 'Yantzaza'],
        'Galápagos': ['Puerto Ayora', 'Puerto Baquerizo Moreno']
    };

    if (regionSelect && provinciaSelect && cantonSelect) {
        regionSelect.addEventListener('change', function() {
            const region = this.value;
            provinciaSelect.innerHTML = '<option value="" disabled selected>Seleccione provincia...</option>';
            cantonSelect.innerHTML = '<option value="" disabled selected>Seleccione cantón...</option>';
            cantonSelect.disabled = true;
            if (provinciasPorRegion[region]) {
                provinciasPorRegion[region].forEach(function(prov) {
                    const opt = document.createElement('option');
                    opt.value = prov;
                    opt.textContent = prov;
                    provinciaSelect.appendChild(opt);
                });
            }
        });
        provinciaSelect.addEventListener('change', function() {
            const provincia = this.value;
            cantonSelect.innerHTML = '<option value="" disabled selected>Seleccione cantón...</option>';
            if (cantonesPorProvincia[provincia]) {
                cantonesPorProvincia[provincia].forEach(function(canton) {
                    const opt = document.createElement('option');
                    opt.value = canton;
                    opt.textContent = canton;
                    cantonSelect.appendChild(opt);
                });
                cantonSelect.disabled = false;
            } else {
                cantonSelect.disabled = true;
            }
        });
    }
    // =============== FIN SCRIPT PROVINCIAS Y CANTONES DINÁMICOS ===============
});