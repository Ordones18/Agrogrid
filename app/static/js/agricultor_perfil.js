// Scripts migrados desde agricultor/perfil_agricultor.html

// =================== HISTORIAL DE VENTAS ===================
document.addEventListener('DOMContentLoaded', function() {
  // --- Tabla desplegable ---
  const toggle = document.getElementById('toggle-historial');
  const cont = document.getElementById('contenedor-historial');
  const icono = document.getElementById('icono-toggle');
  if (cont) {
    // Asegura que inicie cerrado
    cont.classList.remove('abierto');
    let abierto = false;
    toggle.addEventListener('click', function() {
      abierto = !abierto;
      cont.classList.toggle('abierto', abierto);
      icono.style.transform = abierto ? 'rotate(180deg)' : 'rotate(0deg)';
    });
  }
  // --- Cargar historial ventas ---
  fetch('/api/historial_ventas')
    .then(res => res.json())
    .then(historial => {
      const tbody = document.getElementById('tbody-historial-ventas');
      tbody.innerHTML = '';
      if (!historial || historial.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; color:#888;">Aún no tienes ventas registradas.</td></tr>`;
        return;
      }
      historial.forEach(venta => {
        const row = document.createElement('tr');
        row.innerHTML = `
          <td class="col-fecha"><span class="fecha-hora-venta">${venta.fecha_hora_str}</span></td>
          <td class="col-producto">${venta.producto}</td>
          <td class="col-cantidad">${venta.cantidad}</td>
          <td class="col-precio">$${parseFloat(venta.precio_unitario).toFixed(2)}</td>
          <td class="col-total"><span class="total-venta">$${parseFloat(venta.total).toFixed(2)}</span></td>
          <td class="col-comprador">${venta.comprador_nombre ? venta.comprador_nombre : '-'}</td>
          <td class="col-estado">${estadoLegible(venta.estado)}</td>
        `;
        tbody.appendChild(row);
      });

      function estadoLegible(estado) {
        if (!estado) return '-';
        switch (estado) {
          case 'pendiente': return 'Pendiente';
          case 'aceptado': return 'Aceptado';
          case 'en_progreso': return 'En progreso';
          case 'entregado': return 'Entregado';
          default: return estado;
        }
      }
    })
    .catch(() => {
      const tbody = document.getElementById('tbody-historial-ventas');
      tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; color:#d32f2f;">Error al cargar el historial de ventas.</td></tr>`;
    });
});


// =================== SECCIÓN VENTAS TOTALES Y POR PRODUCTO (Gráficos) ===================
document.addEventListener('DOMContentLoaded', function() {
  // Ventas Totales - Gráficos
  fetch('/api/ventas_totales')
    .then(res => res.json())
    .then(data => {
      // Mostrar resumen numérico
      const ventasTotalesGeneral = document.getElementById('ventas-totales-general');
      if (ventasTotalesGeneral) {
        ventasTotalesGeneral.textContent = 'Total general: $' + (data.total_general ? data.total_general.toFixed(2) : '0.00');
      }

      // --- Ventas por Producto ---
      const productos = Object.keys(data.por_producto || {});
      const ventasPorProducto = Object.values(data.por_producto || {});

      if (document.getElementById('grafico-ventas-producto')) {
        const traceProducto = {
          x: ventasPorProducto,
          y: productos,
          type: 'bar',
          orientation: 'h',
          marker: { color: '#4caf50' },
          text: ventasPorProducto.map(v => '$' + v.toFixed(2)),
          textposition: 'auto',
          hovertemplate: '<b>%{y}</b><br>Ventas: <b>$%{x:.2f}</b><extra></extra>',
        };
        const layoutProducto = {
          title: 'Ventas por Producto',
          xaxis: { title: 'Ventas ($)', zeroline: false },
          yaxis: { title: 'Producto', automargin: true },
          margin: { l: 120, r: 30, t: 40, b: 40 },
          plot_bgcolor: '#f9fafb',
          paper_bgcolor: '#f9fafb',
          font: { family: 'Open Sans, sans-serif', size: 14 },
          bargap: 0.25,
          showlegend: false,
          hoverlabel: { bgcolor: '#fff', bordercolor: '#4caf50', font: { color: '#333' } },
        };
        Plotly.newPlot('grafico-ventas-producto', [traceProducto], layoutProducto, {responsive: true, displayModeBar: false});
      }

      // --- Ventas Totales por periodo ---
      const groupbyOptions = {
        semana: data.por_semana || {},
        mes: data.por_mes || {},
        anio: data.por_anio || {}
      };

      function renderVentasTotales(periodo) {
        const ventasPorPeriodo = groupbyOptions[periodo];
        const labels = Object.keys(ventasPorPeriodo);
        const valores = Object.values(ventasPorPeriodo);
        const trace = {
          x: labels,
          y: valores,
          type: 'bar',
          marker: { color: '#1976d2' },
          text: valores.map(v => '$' + v.toFixed(2)),
          textposition: 'auto',
          hovertemplate: '<b>%{x}</b><br>Ventas: <b>$%{y:.2f}</b><extra></extra>',
        };
        const layout = {
          title: 'Ventas Totales por ' + (periodo === 'semana' ? 'Semana' : periodo === 'mes' ? 'Mes' : 'Año'),
          xaxis: { title: periodo.charAt(0).toUpperCase() + periodo.slice(1), tickangle: -45 },
          yaxis: { title: 'Ventas ($)', zeroline: false },
          margin: { l: 60, r: 30, t: 40, b: 80 },
          plot_bgcolor: '#f9fafb',
          paper_bgcolor: '#f9fafb',
          font: { family: 'Open Sans, sans-serif', size: 14 },
          showlegend: false,
          hoverlabel: { bgcolor: '#fff', bordercolor: '#1976d2', font: { color: '#333' } },
          bargap: 0.25,
        };
        if (document.getElementById('grafico-ventas-totales')) {
          Plotly.newPlot('grafico-ventas-totales', [trace], layout, {responsive: true, displayModeBar: false});
        }
      }

      // Inicializar con "mes"
      renderVentasTotales('mes');
      const groupbySelect = document.getElementById('ventas-totales-groupby');
      if (groupbySelect) {
        groupbySelect.addEventListener('change', function() {
          renderVentasTotales(this.value);
        });
      }
    });
});

// =================== SECCIÓN ANALÍTICA: VISTAS A PRODUCTOS ===================
// Este script obtiene los datos de vistas por producto desde la API y renderiza un gráfico interactivo usando Plotly.js.
// Permite filtrar por tipo de producto y muestra tooltips personalizados.

function truncar(str, n) {
  return (str.length > n) ? str.substr(0, n-1) + '…' : str;
}

let productosData = [];
let tiposUnicos = new Set();

function renderGrafico(filtroTipo = "") {
  let productos = productosData;
  if (filtroTipo) {
    productos = productos.filter(p => p.tipo === filtroTipo);
  }
  const nombres = productos.map(p => truncar(p.nombre, 18));
  const nombresFull = productos.map(p => p.nombre);
  const vistas = productos.map(p => p.vistas);
  const tipos = productos.map(p => p.tipo);
  const precios = productos.map(p => p.precio);
  const cantidades = productos.map(p => p.cantidad);
  const unidades = productos.map(p => p.unidad);
  const provincias = productos.map(p => p.provincia);
  const regiones = productos.map(p => p.region);

  // Gradiente de color según vistas
  const minV = Math.min(...vistas);
  const maxV = Math.max(...vistas);
  const colores = vistas.map(v => `rgba(76,175,80,${0.4 + 0.6 * ((v - minV) / (maxV - minV || 1))})`);
  // El más visto en naranja
  if (vistas.length > 0) {
    const idx = vistas.indexOf(maxV);
    if (idx !== -1) colores[idx] = '#ff9800';
  }

  const trace = {
    x: vistas,
    y: nombres,
    type: 'bar',
    orientation: 'h',
    marker: { color: colores },
    text: vistas.map(String),
    textposition: 'inside',
    hovertemplate:
      '<b>%{customdata[0]}</b><br>' +
      'Vistas: <b>%{x}</b><br>' +
      'Tipo: %{customdata[1]}<br>' +
      'Precio: $%{customdata[2]:.2f} / %{customdata[5]}<br>' +
      'Cantidad: %{customdata[3]} %{customdata[5]}<br>' +
      'Provincia: %{customdata[6]}<br>' +
      'Región: %{customdata[7]}<extra></extra>',
    customdata: productos.map((p, i) => [nombresFull[i], p.tipo, p.precio, p.cantidad, p.vistas, p.unidad, p.provincia, p.region]),
  };
  const layout = {
    title: 'Vistas por Producto',
    xaxis: { title: 'Vistas', zeroline: false },
    yaxis: { title: 'Producto', automargin: true },
    margin: { l: 140, r: 30, t: 60, b: 40 },
    plot_bgcolor: '#f9fafb',
    paper_bgcolor: '#f9fafb',
    font: { family: 'Open Sans, sans-serif', size: 14 },
    bargap: 0.25,
    showlegend: false,
    hoverlabel: { bgcolor: '#fff', bordercolor: '#4caf50', font: { color: '#333' } },
    transition: { duration: 500, easing: 'cubic-in-out' },
  };
  Plotly.newPlot('plotly-vistas-productos', [trace], layout, {responsive: true, displayModeBar: true, displaylogo: false, modeBarButtonsToRemove: ['sendDataToCloud']});

  // Tooltips para nombres truncados
  setTimeout(() => {
    document.querySelectorAll('#plotly-vistas-productos .ytick text').forEach((el, i) => {
      el.setAttribute('title', nombresFull[i]);
    });
  }, 500);
}

document.addEventListener('DOMContentLoaded', function() {
  fetch('/api/vistas_productos')
    .then(response => response.json())
    .then(data => {
      productosData = data.productos || [];
      // Llenar el filtro de tipo
      tiposUnicos = new Set(productosData.map(p => p.tipo));
      const filtro = document.getElementById('filtro-tipo');
      filtro.innerHTML = '<option value="">Todos</option>' + Array.from(tiposUnicos).map(t => `<option value="${t}">${t}</option>`).join('');
      filtro.addEventListener('change', function() {
        renderGrafico(this.value);
      });
      renderGrafico();
    });
});


// =================== INICIALIZACIÓN WIDGET DE TAXONOMÍA ===================
document.addEventListener('DOMContentLoaded', function() {
  // Inicializar el nuevo selector de taxonomía
  const taxonomiaSelector = new TaxonomiaSelector({
    onSelect: function(selectedPath) {
      const form = document.querySelector('.product-form');
      const submitBtn = form.querySelector('button[type="submit"]');
      if (selectedPath && selectedPath.producto) {
        submitBtn.disabled = false;
        submitBtn.style.opacity = '1';
      } else {
        submitBtn.disabled = true;
        submitBtn.style.opacity = '0.6';
      }
    }
  });
  // Deshabilitar el botón de envío inicialmente
  const form = document.querySelector('.product-form');
  if (form) {
    const submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.style.opacity = '0.6';
      // Validación adicional antes del envío
      form.addEventListener('submit', function(e) {
        const selectedProduct = taxonomiaSelector.getSelectedProduct();
        if (!selectedProduct || !selectedProduct.categoria || !selectedProduct.subcategoria || !(selectedProduct.producto && selectedProduct.producto.length > 0)) {
          e.preventDefault();
          alert('Por favor, seleccione y/o escriba un producto de la clasificación.');
          return false;
        }
      });
    }
  }
});

// Otros scripts migrados se agregarán aquí paso a paso.
