// JS para el perfil de transportista: maneja viajes pendientes y asignados

document.addEventListener('DOMContentLoaded', function() {
    // Eliminar vehículo por AJAX
    document.addEventListener('submit', function(e) {
        const form = e.target.closest('.vehiculo-eliminar-js');
        if (form) {
            e.preventDefault();
            const url = form.action;
            fetch(url, { method: 'POST', headers: { 'X-Requested-With': 'XMLHttpRequest' } })
                .then(res => {
                    if (res.redirected) {
                        window.location.href = res.url;
                        return;
                    }
                    return res.text();
                })
                .then(() => {
                    // Eliminar tarjeta visualmente
                    const card = form.closest('.vehiculo-card');
                    if (card) card.remove();
                    // Mostrar mensaje
                    const msgDiv = document.getElementById('mensaje-vehiculo-js');
                    if (msgDiv) {
                        msgDiv.textContent = 'Vehículo eliminado correctamente';
                        msgDiv.style.display = 'block';
                        msgDiv.style.background = '#d2f8e5';
                        msgDiv.style.color = '#229e60';
                        msgDiv.style.border = '1px solid #43b97f';
                        msgDiv.style.borderRadius = '7px';
                        msgDiv.style.padding = '0.6em 1em';
                        msgDiv.style.marginBottom = '0.8em';
                        setTimeout(() => { msgDiv.style.display = 'none'; }, 2500);
                    }
                });
        }
    });
    // Cargar viajes pendientes
    fetch('/api/viajes_pendientes')
        .then(res => res.json())
        .then(viajes => {
            const tbody = document.getElementById('tbody-viajes-pendientes');
            tbody.innerHTML = '';
            if (!viajes || viajes.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7" class="empty-state">No hay viajes pendientes.</td></tr>';
                return;
            }
            viajes.forEach(viaje => {
                const tr = document.createElement('tr');
                let valor = viaje.valor_envio;
                if (valor === undefined && viaje.costo_envio !== undefined) valor = viaje.costo_envio;
                if (valor === undefined && viaje.total !== undefined) valor = viaje.total;
                let valorStr = valor !== undefined && valor !== null ? `$${parseFloat(valor).toLocaleString('es-EC', {minimumFractionDigits:2})}` : '-';
                tr.innerHTML = `
                    <td>${viaje.origen || ''}</td>
                    <td>${viaje.destino || ''}</td>
                    <td>${viaje.productos || ''}</td>
                    <td>${viaje.agricultor || ''}</td>
                    <td>${viaje.comprador || ''}</td>
                    <td>${valorStr}</td>
                    <td>
                        <button class="btn-aceptar-viaje" data-id="${viaje.id}"><i class="fas fa-check"></i> Aceptar</button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        });

    // Cargar viajes asignados
    fetch('/api/viajes_asignados')
        .then(res => res.json())
        .then(viajes => {
            const tbody = document.getElementById('tbody-viajes-asignados');
            tbody.innerHTML = '';
            if (!viajes || viajes.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" class="empty-state">No tienes viajes asignados.</td></tr>';
                return;
            }
            viajes.forEach(viaje => {
                const tr = document.createElement('tr');
                let valor = viaje.valor_envio;
                if (valor === undefined && viaje.costo_envio !== undefined) valor = viaje.costo_envio;
                if (valor === undefined && viaje.total !== undefined) valor = viaje.total;
                let valorStr = valor !== undefined && valor !== null ? `$${parseFloat(valor).toLocaleString('es-EC', {minimumFractionDigits:2})}` : '-';
                tr.innerHTML = `
                    <td>${viaje.origen || ''}</td>
                    <td>${viaje.destino || ''}</td>
                    <td>${viaje.productos || ''}</td>
                    <td>${viaje.estado || ''}</td>
                    <td>${valorStr}</td>
                    <td>
                        ${viaje.estado === 'en_progreso' ? `<button class="btn-marcar-entregado" data-id="${viaje.id}"><i class="fas fa-flag-checkered"></i> Marcar Entregado</button>` : ''}
                    </td>
                `;
                tbody.appendChild(tr);
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
                        // Actualiza la gráfica de ganancias sin recargar la página
                        if (window.recargarGananciasYActualizar) {
                            window.recargarGananciasYActualizar();
                        }
                    } else {
                        btn.disabled = false;
                        alert(resp.message || 'Error al marcar como entregado');
                    }
                });
        }
    });
});
