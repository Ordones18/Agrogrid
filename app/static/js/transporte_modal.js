// JS para modal de cálculo de transporte
// Requiere endpoint /api/calcular_transporte y /api/ubicaciones_catalogo

document.addEventListener('DOMContentLoaded', function() {
  // Estructura de ubicaciones (región > provincia > cantón)
  let ubicaciones = {};
  fetch('/api/ubicacion/estructura')
    .then(res => res.json())
    .then(data => {
      ubicaciones = data;
      // Para cada bloque de transporte (uno por cantón de origen)
      document.querySelectorAll('.bloque-transporte-canton').forEach(function(bloque) {
        const form = bloque.querySelector('.formTransporte');
        const regionSelect = form.querySelector('.regionSelect');
        const provinciaSelect = form.querySelector('.provinciaSelect');
        const cantonSelect = form.querySelector('.cantonSelect');
        const resultadoDiv = bloque.querySelector('.resultadoTransporte');
        const cantonOrigen = form.getAttribute('data-canton');

        // Poblar regiones destino
        regionSelect.innerHTML = '<option value="">Seleccione región</option>';
        Object.keys(ubicaciones).forEach(region => {
          regionSelect.innerHTML += `<option value="${region}">${region}</option>`;
        });
        regionSelect.onchange = function() {
          provinciaSelect.innerHTML = '<option value="">Seleccione provincia</option>';
          cantonSelect.innerHTML = '<option value="">Seleccione cantón</option>';
          if (ubicaciones[this.value]) {
            Object.keys(ubicaciones[this.value]).forEach(prov => {
              provinciaSelect.innerHTML += `<option value="${prov}">${prov}</option>`;
            });
          }
        };
        provinciaSelect.onchange = function() {
          cantonSelect.innerHTML = '<option value="">Seleccione cantón</option>';
          if (ubicaciones[regionSelect.value] && ubicaciones[regionSelect.value][this.value]) {
            ubicaciones[regionSelect.value][this.value].forEach(canton => {
              cantonSelect.innerHTML += `<option value="${canton}">${canton}</option>`;
            });
          }
        };

        // Calcular transporte para este bloque
        form.onsubmit = function(e) {
          e.preventDefault();
          resultadoDiv.innerHTML = '<span style="color:#388e3c;">Calculando...</span>';
          const cantonDestino = cantonSelect.value;
          if (!cantonDestino) {
            resultadoDiv.innerHTML = '<span style="color:#c00">Seleccione un cantón destino.</span>';
            return;
          }
          fetch('/api/calcular_transporte', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ origen: cantonOrigen, destino: cantonDestino })
          })
          .then(res => res.json())
          .then(data => {
            if (data.distancia && data.ruta) {
              let resultadoHtml = `<b>Origen:</b> ${cantonOrigen} <b>→ Destino:</b> ${cantonDestino}<br>
                <b>Distancia:</b> ${data.distancia.toFixed(2)} km<br>
                <b>Tiempo estimado:</b> ${data.tiempo_legible} (${data.tiempo_min} min)<br>
                <b>Costo de envío:</b> $${data.costo_envio.toFixed(2)}<br>
                <b>Ruta:</b> ${data.ruta.join(' → ')}<br>
                <b>Tipo:</b> ${data.tipos.join(', ')}`;
              // Sumar costo de envío al total del carrito
              const totalDiv = document.querySelector('.carrito-total-final');
              if (totalDiv) {
                const match = totalDiv.textContent.match(/\$([0-9,.]+)/);
                if (match) {
                  const total = parseFloat(match[1].replace(',', ''));
                  const newTotal = total + data.costo_envio;
                  totalDiv.innerHTML = `Total: $${newTotal.toFixed(2)}`;
                  // Guardar costo de envío en sesión
                  fetch('/api/guardar_envio', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ costo_envio: data.costo_envio })
                  });
                }
              }
              resultadoDiv.innerHTML = resultadoHtml;
            } else {
              resultadoDiv.innerHTML = `<span style="color:#c00">Ruta no encontrada entre <b>${cantonOrigen}</b> y <b>${cantonDestino}</b></span>`;
            }
          })
          .catch(() => {
            resultadoDiv.innerHTML = '<span style="color:#c00">Error al calcular</span>';
          });
        };
      });
    });
});

