// JS futuro para cargar y animar entradas del blog

// Expansión de artículos "Leer más"
document.addEventListener('DOMContentLoaded', function() {
  const cards = document.querySelectorAll('.blog-card');
  cards.forEach(card => {
    const btn = card.querySelector('.blog-leer-mas');
    if (btn) {
      btn.addEventListener('click', function() {
        // Cierra otros
        cards.forEach(c => { if(c !== card) { c.classList.remove('open'); c.querySelector('.blog-leer-mas').classList.remove('open'); }});
        // Toggle actual
        card.classList.toggle('open');
        btn.classList.toggle('open');
      });
    }
  });
});
