// Vista rápida de productos

document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('quickViewModal');
    const closeBtn = document.querySelector('.quick-view-close');
    const quickViewBtns = document.querySelectorAll('.btn-quick-view-light');

    function openModal(data) {
        document.getElementById('qv-imagen').src = data.imagen;
        document.getElementById('qv-nombre').textContent = data.nombre;
        document.getElementById('qv-tipo').textContent = data.tipo;
        document.getElementById('qv-region').textContent = data.region;
        document.getElementById('qv-provincia').textContent = data.provincia;
        document.getElementById('qv-precio').textContent = data.precio;
        document.getElementById('qv-cantidad').textContent = data.cantidad;
        document.getElementById('qv-descripcion').textContent = data.descripcion;
        modal.style.display = 'block';
    }

    quickViewBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const productoId = btn.getAttribute('data-producto-id');
            const data = {
                nombre: btn.getAttribute('data-nombre'),
                imagen: btn.getAttribute('data-imagen'),
                tipo: btn.getAttribute('data-tipo'),
                region: btn.getAttribute('data-region'),
                provincia: btn.getAttribute('data-provincia'),
                precio: btn.getAttribute('data-precio'),
                cantidad: btn.getAttribute('data-cantidad'),
                descripcion: btn.getAttribute('data-descripcion')
            };
            // Registrar vista rápida
            if (productoId) {
                fetch('/api/registrar_vista_rapida', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ producto_id: productoId })
                });
            }
            openModal(data);
        });
    });

    closeBtn.addEventListener('click', function() {
        modal.style.display = 'none';
    });

    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    };
});
