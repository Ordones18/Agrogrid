// --- Ventas y Ganancias Chart ---
const ventasSeries = window._ventasSeries;
let periodo = 'mes';
let chart;
function renderChartAdmin() {
  const ctx = document.getElementById('graficaVentasAdmin').getContext('2d');
  const labels = ventasSeries[periodo].labels;
  const ventas = ventasSeries[periodo].ventas;
  const ganancias = ventasSeries[periodo].ganancias;
  if (chart) chart.destroy();
  chart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [
        { label: 'Ventas totales', data: ventas, backgroundColor: '#1976d2', borderRadius: 6, maxBarThickness: 40 },
        { label: 'Ganancias (1%)', data: ganancias, backgroundColor: '#43a047', borderRadius: 6, maxBarThickness: 40 }
      ]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: 'top' },
        tooltip: {
          callbacks: {
            label: function(context) {
              let v = context.parsed.y;
              return (context.dataset.label === 'Ganancias (1%)' ? 'G: $' : 'V: $') + v.toLocaleString('es-EC', {minimumFractionDigits:2});
            }
          }
        }
      },
      scales: {
        x: { title: { display: true, text: periodo.charAt(0).toUpperCase() + periodo.slice(1) }, grid: { display: false } },
        y: { beginAtZero: true, title: { display: true, text: 'USD' } }
      }
    }
  });
}
document.getElementById('ventas-periodo').addEventListener('change', function() {
  periodo = this.value;
  renderChartAdmin();
});
renderChartAdmin();
