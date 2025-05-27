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
});