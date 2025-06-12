// favoritos.js
// Manejo de favoritos (agregar/quitar) y mensajes flotantes en productos

document.addEventListener('DOMContentLoaded', function() {
    // --- Manejo de favoritos en grilla de productos ---
    document.querySelectorAll('.btn-favorito').forEach(function(btn) {
        btn.addEventListener('click', function() {
            const productoId = this.getAttribute('data-producto-id');
            const icon = this.querySelector('i');
            const esFavorito = icon.classList.contains('fa-heart') && icon.classList.contains('favorito-activo');
            const url = esFavorito ? `/favoritos/quitar/${productoId}` : `/favoritos/agregar/${productoId}`;
            fetch(url, {method: 'POST', headers: {'X-Requested-With': 'XMLHttpRequest'}})
                .then(r => r.json())
                .then(data => {
                    if(data.success) {
                        icon.classList.toggle('favorito-activo');
                        icon.classList.toggle('fas');
                        icon.classList.toggle('far');
                        if (!esFavorito) {
                            mostrarMensaje('Agregado a favoritos correctamente', 'success');
                        } else {
                            mostrarMensaje('Eliminado de favoritos correctamente', 'success');
                        }
                    }
                });
        });
    });

    // --- Función global para mostrar mensajes flotantes ---
    window.mostrarMensaje = function(texto, tipo) {
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
    };
});
