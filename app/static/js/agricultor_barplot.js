// Gráfica de Total General de ventas del agricultor (Chart.js)
// Solo para la sección de Total General, no afecta ventas por producto ni vistas

document.addEventListener('DOMContentLoaded', function() {
  const ventasSelect = document.getElementById('ventas-totales-groupby');
  const ventasSeries = JSON.parse(document.getElementById('barplot-ventas-series-json').textContent);
  const ctxVentas = document.getElementById('graficaVentasTotales').getContext('2d');
  let chartVentas;

  function crearChartVentas(labels, data, label) {
    if (chartVentas) chartVentas.destroy();
    chartVentas = new Chart(ctxVentas, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [{
          label: 'Ventas totales',
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
            title: { display: true, text: 'Ventas totales (USD)' },
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

  function actualizarSerieVentas(serie) {
    const datos = ventasSeries[serie];
    crearChartVentas(datos.labels, datos.data, serie);
  }

  ventasSelect.addEventListener('change', function() {
    actualizarSerieVentas(this.value);
  });

  // Inicializa con mes
  actualizarSerieVentas('mes');
});
