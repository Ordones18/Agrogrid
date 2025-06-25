// Lógica de calificación migrada a página dedicada. Aquí puedes agregar otros scripts del perfil si los necesitas.

// Espera a que el DOM esté listo
window.addEventListener('DOMContentLoaded', function () {
  // Datos globales inyectados por Jinja2
  if (typeof window.comprasAgregadas === 'undefined') return;

  // --- Barplot de gasto por periodo ---
  const comprasPorPeriodo = {
    'dia': window.comprasAgregadas.por_dia,
    'semana': window.comprasAgregadas.por_semana,
    'mes': window.comprasAgregadas.por_mes,
    'anio': window.comprasAgregadas.por_anio
  };

  function getBarplotData(periodo) {
    const data = comprasPorPeriodo[periodo] || {};
    let etiquetas = Object.keys(data);
    if (periodo === 'dia') {
      etiquetas = etiquetas.sort(); // fechas ordenadas
    } else {
      etiquetas = etiquetas.sort();
    }
    const valores = etiquetas.map(k => data[k]);
    return { etiquetas, valores };
  }

  const ctxBar = document.getElementById('compras-barplot').getContext('2d');
  let barChart;

  function renderBarplot(periodo) {
    const { etiquetas, valores } = getBarplotData(periodo);
    if (barChart) barChart.destroy();
    barChart = new Chart(ctxBar, {
      type: 'bar',
      data: {
        labels: etiquetas,
        datasets: [{
          label: 'Gasto ($)',
          data: valores,
          backgroundColor: '#43b97f',
        }]
      },
      options: {
        responsive: false,
        animation: false,
        interaction: { mode: 'nearest', intersect: false },
        plugins: { legend: { display: false } },
        scales: {
          x: {
            beginAtZero: false,
            grid: { color: '#e8f6ef' },
            ticks: { color: '#229e60', font: { weight: 'bold', size: 11 }, autoSkip: etiquetas.length > 16, maxTicksLimit: 16 }
          },
          y: {
            beginAtZero: true,
            grid: { color: '#e8f6ef' },
            ticks: { color: '#229e60', font: { weight: 'bold' } }
          }
        }
      }
    });
  }

  // Select para periodo
  const periodoSelect = document.getElementById('compras-periodo-select');
  periodoSelect.addEventListener('change', function () {
    renderBarplot(this.value);
  });
  renderBarplot(periodoSelect.value);

  // --- Bar horizontal: productos más comprados por gasto ---
  const topGasto = window.top5Gasto || [];
  const barGastoLabels = topGasto.map(x => x[0]);
  const barGastoData = topGasto.map(x => x[1]);
  const barColors = ['#43b97f','#229e60','#388e3c','#b0e5c7','#a6d8b8'];

  const ctxBarGasto = document.getElementById('compras-pie').getContext('2d');
  new Chart(ctxBarGasto, {
    type: 'bar',
    data: {
      labels: barGastoLabels,
      datasets: [{
        label: 'Gasto ($)',
        data: barGastoData,
        backgroundColor: barColors,
        borderRadius: 8,
        maxBarThickness: 36,
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: false,
      plugins: {
        legend: { display: false },
        tooltip: { enabled: true }
      },
      scales: {
        x: {
          beginAtZero: true,
          grid: { color: '#e8f6ef' },
          ticks: { color: '#229e60', font: { weight: 'bold' } }
        },
        y: {
          grid: { display: false },
          ticks: { color: '#229e60', font: { weight: 'bold' } }
        }
      }
    }
  });

  // --- Bar horizontal: productos más comprados por cantidad ---
  const topCantidad = window.top5Cantidad || [];
  const barCantidadLabels = topCantidad.map(x => x[0]);
  const barCantidadData = topCantidad.map(x => x[1]);
  const ctxBarCantidad = document.getElementById('compras-pie-cantidad').getContext('2d');
  new Chart(ctxBarCantidad, {
    type: 'bar',
    data: {
      labels: barCantidadLabels,
      datasets: [{
        label: 'Cantidad',
        data: barCantidadData,
        backgroundColor: barColors,
        borderRadius: 8,
        maxBarThickness: 36,
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: false,
      plugins: {
        legend: { display: false },
        tooltip: { enabled: true }
      },
      scales: {
        x: {
          beginAtZero: true,
          grid: { color: '#e8f6ef' },
          ticks: { color: '#229e60', font: { weight: 'bold' } }
        },
        y: {
          grid: { display: false },
          ticks: { color: '#229e60', font: { weight: 'bold' } }
        }
      }
    }
  });
});


        




