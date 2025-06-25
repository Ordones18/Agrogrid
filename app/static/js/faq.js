// JS para acordeón de preguntas frecuentes AgroGrid - FIX CLICK

document.addEventListener('DOMContentLoaded', function () {
  const items = document.querySelectorAll('.faq-item');
  items.forEach(item => {
    const btn = item.querySelector('.faq-question');
    const answer = item.querySelector('.faq-answer');
    btn.type = 'button';
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      // Cierra todos los demás
      items.forEach(i => {
        if(i !== item) {
          i.classList.remove('active');
          i.querySelector('.faq-answer').classList.remove('active');
          i.querySelector('.faq-question').setAttribute('aria-expanded', 'false');
        }
      });
      // Toggle el actual
      const isActive = item.classList.toggle('active');
      answer.classList.toggle('active', isActive);
      btn.setAttribute('aria-expanded', isActive ? 'true' : 'false');
    });
    // Accesibilidad: abrir/cerrar con Enter/Espacio
    btn.addEventListener('keydown', function(e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        btn.click();
      }
    });
    btn.setAttribute('tabindex', '0');
    btn.setAttribute('aria-expanded', 'false');
    btn.addEventListener('focus', function() {
      btn.style.outline = '2px solid #1e7c4c';
    });
    btn.addEventListener('blur', function() {
      btn.style.outline = '';
    });
  });
});
