// Selector de Ubicación: Región > Provincia > Cantón
// Este script asume que existe una API en /api/ubicacion/estructura que retorna la estructura completa
// Similar al de taxonomía, pero para selects dependientes

(function() {
  let ubicacionData = {};

  function loadEstructuraUbicacion() {
    fetch('/api/ubicacion/estructura')
      .then(res => res.json())
      .then(data => {
        ubicacionData = data;
        fillRegiones();
      });
  }

  function fillRegiones() {
    const regionSel = document.getElementById('regionSelector');
    regionSel.innerHTML = '<option value="" disabled selected>Seleccione región...</option>';
    Object.keys(ubicacionData).forEach(region => {
      const opt = document.createElement('option');
      opt.value = region;
      opt.textContent = region;
      regionSel.appendChild(opt);
    });
    regionSel.disabled = false;
    document.getElementById('provinciaSelector').disabled = true;
    document.getElementById('cantonSelector').disabled = true;
  }

  function fillProvincias(region) {
    const provinciaSel = document.getElementById('provinciaSelector');
    provinciaSel.innerHTML = '<option value="" disabled selected>Seleccione provincia...</option>';
    if (!region || !ubicacionData[region]) {
      provinciaSel.disabled = true;
      document.getElementById('cantonSelector').disabled = true;
      return;
    }
    Object.keys(ubicacionData[region]).forEach(provincia => {
      const opt = document.createElement('option');
      opt.value = provincia;
      opt.textContent = provincia;
      provinciaSel.appendChild(opt);
    });
    provinciaSel.disabled = false;
    document.getElementById('cantonSelector').disabled = true;
  }

  function fillCantones(region, provincia) {
    const cantonSel = document.getElementById('cantonSelector');
    cantonSel.innerHTML = '<option value="" disabled selected>Seleccione cantón...</option>';
    if (!region || !provincia || !ubicacionData[region] || !ubicacionData[region][provincia]) {
      cantonSel.disabled = true;
      return;
    }
    ubicacionData[region][provincia].forEach(canton => {
      const opt = document.createElement('option');
      opt.value = canton;
      opt.textContent = canton;
      cantonSel.appendChild(opt);
    });
    cantonSel.disabled = false;
  }

  document.addEventListener('DOMContentLoaded', function() {
    if (!document.getElementById('regionSelector')) return;
    loadEstructuraUbicacion();

    document.getElementById('regionSelector').addEventListener('change', function() {
      fillProvincias(this.value);
      document.getElementById('region').value = this.value;
      document.getElementById('provincia').value = '';
      document.getElementById('canton').value = '';
    });
    document.getElementById('provinciaSelector').addEventListener('change', function() {
      const region = document.getElementById('regionSelector').value;
      fillCantones(region, this.value);
      document.getElementById('provincia').value = this.value;
      document.getElementById('canton').value = '';
    });
    document.getElementById('cantonSelector').addEventListener('change', function() {
      document.getElementById('canton').value = this.value;
    });
  });
})();
