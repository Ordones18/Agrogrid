// JS exclusivo para la ventana de calificación de pedido
window.addEventListener('DOMContentLoaded', function() {
  const estrellas = document.querySelectorAll('.estrella');
  const inputCalif = document.getElementById('input-calificacion');
  const form = document.getElementById('form-calificar');
  let seleccion = parseInt(inputCalif.value) || 0;

  estrellas.forEach((estrella, idx) => {
    estrella.addEventListener('mouseenter', () => {
      for (let i = 0; i < estrellas.length; i++) {
        if (i <= idx) {
          estrellas[i].classList.add('selected');
        } else {
          estrellas[i].classList.remove('selected');
        }
      }
    });
    estrella.addEventListener('mouseleave', () => {
      for (let i = 0; i < estrellas.length; i++) {
        if (i < seleccion) {
          estrellas[i].classList.add('selected');
        } else {
          estrellas[i].classList.remove('selected');
        }
      }
    });
    estrella.addEventListener('click', () => {
      seleccion = idx + 1;
      inputCalif.value = seleccion;
      for (let i = 0; i < estrellas.length; i++) {
        if (i < seleccion) {
          estrellas[i].classList.add('selected');
        } else {
          estrellas[i].classList.remove('selected');
        }
      }
    });
  });
  // Inicializa visual correctamente según el valor actual (por si viene de backend)
  for (let i = 0; i < estrellas.length; i++) {
    if (i < seleccion) {
      estrellas[i].classList.add('selected');
    } else {
      estrellas[i].classList.remove('selected');
    }
  }

  if(form) {
    form.addEventListener('submit', function(e) {
      if(seleccion === 0) {
        e.preventDefault();
        alert('Por favor selecciona una calificación.');
      }
    });
  }
});
