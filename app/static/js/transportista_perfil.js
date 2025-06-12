// JS para el perfil de transportista: maneja viajes pendientes y asignados

document.addEventListener('DOMContentLoaded', function() {
    // Cargar viajes pendientes
    fetch('/api/viajes_pendientes')
        .then(res => res.json())
        .then(viajes => {
            const tbody = document.getElementById('tbody-viajes-pendientes');
            tbody.innerHTML = '';
            if (!viajes || viajes.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" class="empty-state">No hay viajes pendientes.</td></tr>';
                return;
            }
            viajes.forEach(viaje => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${viaje.origen}</td>
                    <td>${viaje.destino}</td>
                    <td>${viaje.productos}</td>
                    <td>${viaje.agricultor}</td>
                    <td>${viaje.comprador}</td>
                    <td><button class="btn-aceptar-viaje" data-id="${viaje.id}"><i class="fas fa-check"></i> Aceptar</button></td>
                `;
                tbody.appendChild(row);
            });
        });

    // Cargar viajes asignados
    fetch('/api/viajes_asignados')
        .then(res => res.json())
        .then(viajes => {
            const tbody = document.getElementById('tbody-viajes-asignados');
            tbody.innerHTML = '';
            if (!viajes || viajes.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" class="empty-state">No tienes viajes asignados.</td></tr>';
                return;
            }
            viajes.forEach(viaje => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${viaje.origen}</td>
                    <td>${viaje.destino}</td>
                    <td>${viaje.productos}</td>
                    <td>${viaje.estado}</td>
                    <td>
                        ${viaje.estado === 'en_progreso' ? `<button class="btn-marcar-entregado" data-id="${viaje.id}"><i class="fas fa-flag-checkered"></i> Marcar Entregado</button>` : ''}
                    </td>
                `;
                tbody.appendChild(row);
            });
        });

    // Acción aceptar viaje
    document.addEventListener('click', function(e) {
        if (e.target.closest('.btn-aceptar-viaje')) {
            const btn = e.target.closest('.btn-aceptar-viaje');
            const viajeId = btn.getAttribute('data-id');
            btn.disabled = true;
            fetch(`/api/aceptar_viaje/${viajeId}`, { method: 'POST' })
                .then(res => res.json())
                .then(resp => {
                    if (resp.success) {
                        btn.textContent = '¡Aceptado!';
                        btn.classList.add('btn-success');
                        setTimeout(() => location.reload(), 1000);
                    } else {
                        btn.disabled = false;
                        alert(resp.message || 'Error al aceptar viaje');
                    }
                });
        }
    });

    // Acción marcar como entregado
    document.addEventListener('click', function(e) {
        if (e.target.closest('.btn-marcar-entregado')) {
            const btn = e.target.closest('.btn-marcar-entregado');
            const viajeId = btn.getAttribute('data-id');
            btn.disabled = true;
            fetch(`/api/marcar_entregado/${viajeId}`, { method: 'POST' })
                .then(res => res.json())
                .then(resp => {
                    if (resp.success) {
                        btn.textContent = '¡Entregado!';
                        btn.classList.add('btn-success');
                        setTimeout(() => location.reload(), 1000);
                    } else {
                        btn.disabled = false;
                        alert(resp.message || 'Error al marcar como entregado');
                    }
                });
        }
    });
});
