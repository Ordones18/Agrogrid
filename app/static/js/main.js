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
    if (regionSelect && provinciaSelect) {
        regionSelect.addEventListener('change', function() {
            const region = this.value;
            // Limpia las opciones actuales
            provinciaSelect.innerHTML = '<option value="" disabled selected>Seleccione provincia...</option>';
            if (provinciasPorRegion[region]) {
                provinciasPorRegion[region].forEach(function(prov) {
                    const opt = document.createElement('option');
                    opt.value = prov;
                    opt.textContent = prov;
                    provinciaSelect.appendChild(opt);
                });
            }
        });
    }
    // =============== FIN SCRIPT PROVINCIAS DINÁMICAS ===============
});