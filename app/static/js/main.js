// Espera a que el contenido del DOM esté cargado antes de ejecutar el código
document.addEventListener('DOMContentLoaded', function() {
    // --- Menú móvil ---
    const toggle = document.querySelector('.mobile-menu-toggle');
    const nav = document.querySelector('.navigation');
    if (toggle && nav) {
        toggle.addEventListener('click', function() {
            nav.classList.toggle('active');
        });
    }

    // --- Quitar favorito AJAX ---
    document.querySelectorAll('.form-quitar-favorito').forEach(function(form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const action = form.getAttribute('action');
            fetch(action, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                credentials: 'same-origin'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Eliminar la tarjeta del DOM
                    form.closest('.favorito-profile-card').remove();
                    mostrarMensaje('Eliminado de favoritos correctamente', 'success');
                } else {
                    mostrarMensaje('No se pudo eliminar de favoritos', 'error');
                }
            })
            .catch(() => mostrarMensaje('Error de red', 'error'));
        });
    });

    // Función para mostrar mensaje flotante
    function mostrarMensaje(texto, tipo) {
        let div = document.createElement('div');
        div.className = 'alerta-flotante alerta-' + tipo;
        div.innerText = texto;
        document.body.appendChild(div);
        setTimeout(() => {
            div.classList.add('visible');
        }, 10);
        setTimeout(() => {
            div.classList.remove('visible');
            setTimeout(() => div.remove(), 300);
        }, 2000);
    }
});

