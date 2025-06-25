// JS para animaciones o interacciones del Centro de Ayuda
// Por ejemplo, despliegue de secciones o scroll a preguntas frecuentes

// Animación acordeón para preguntas rápidas

document.addEventListener('DOMContentLoaded', function() {
  const items = document.querySelectorAll('.ayuda-quick-item');
  items.forEach(item => {
    const btn = item.querySelector('.ayuda-quick-q');
    btn.addEventListener('click', function() {
      // Cierra otros
      items.forEach(i => { if(i !== item) i.classList.remove('open'); });
      // Toggle actual
      item.classList.toggle('open');
    });
  });
});
