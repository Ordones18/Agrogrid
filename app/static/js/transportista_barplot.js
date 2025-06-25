// Gráfico interactivo de pedidos entregados con Chart.js

document.addEventListener('DOMContentLoaded', function() {
  // --- Pedidos entregados ---
  const select = document.getElementById('barplot-select');
  const seriesData = JSON.parse(document.getElementById('barplot-series-json').textContent);
  const ctx = document.getElementById('graficaPedidosEntregados').getContext('2d');
  let chart;

  function crearChart(labels, data, label) {
    if (chart) chart.destroy();
    chart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Pedidos entregados',
          data: data,
          backgroundColor: '#43b97f',
          borderRadius: 6,
          maxBarThickness: 40,
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { display: false },
          tooltip: { enabled: true }
        },
        scales: {
          x: {
            title: { display: true, text: label.charAt(0).toUpperCase() + label.slice(1) },
            grid: { display: false }
          },
          y: {
            beginAtZero: true,
            title: { display: true, text: 'Cantidad' },
            ticks: { precision:0 }
          }
        }
      }
    });
  }

  function actualizarSerie(serie) {
    const datos = seriesData[serie];
    crearChart(datos.labels, datos.data, serie);
  }

  select.addEventListener('change', function() {
    actualizarSerie(this.value);
  });

  // Inicializa con semana
  actualizarSerie('semana');

  // --- Ganancias ---
  const gananciasSelect = document.getElementById('ganancias-select');
  let gananciasSeries = JSON.parse(document.getElementById('barplot-ganancias-series-json').textContent);
  const ctxGanancias = document.getElementById('graficaGanancias').getContext('2d');
  let chartGanancias;

  function crearChartGanancias(labels, data, label) {
    if (chartGanancias) chartGanancias.destroy();
    chartGanancias = new Chart(ctxGanancias, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Dinero ganado',
          data: data,
          backgroundColor: '#1e88e5',
          borderRadius: 6,
          maxBarThickness: 40,
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { display: false },
          tooltip: {
            enabled: true,
            callbacks: {
              label: function(context) {
                let value = context.parsed.y;
                return ' $' + value.toLocaleString('es-EC', { minimumFractionDigits: 2 });
              }
            }
          }
        },
        scales: {
          x: {
            title: { display: true, text: label.charAt(0).toUpperCase() + label.slice(1) },
            grid: { display: false }
          },
          y: {
            beginAtZero: true,
            title: { display: true, text: 'Dinero ganado (USD)' },
            ticks: {
              callback: function(value) {
                return '$' + value.toLocaleString('es-EC', { minimumFractionDigits: 0 });
              }
            }
          }
        }
      }
    });
  }

  function actualizarSerieGanancias(serie) {
    const datos = gananciasSeries[serie];
    crearChartGanancias(datos.labels, datos.data, serie);
  }

  // Permite recargar ganancias desde el backend vía API
  async function recargarGananciasYActualizar(serie = null) {
    try {
      const res = await fetch('/api/ganancias_transportista');
      if (!res.ok) return;
      gananciasSeries = await res.json();
      const actual = serie || gananciasSelect.value || 'semana';
      actualizarSerieGanancias(actual);
    } catch (e) {
      // Silenciar error
    }
  }

  // Expone la función globalmente para que otros scripts la llamen
  window.recargarGananciasYActualizar = recargarGananciasYActualizar;

  gananciasSelect.addEventListener('change', function() {
    actualizarSerieGanancias(this.value);
  });

  // Inicializa con semana
  actualizarSerieGanancias('semana');

  // Si otros scripts disparan window.recargarGananciasYActualizar(), la gráfica se actualizará sin recargar la página
});
