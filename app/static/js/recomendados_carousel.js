// Carousel de recomendados para productos.html
window.addEventListener('DOMContentLoaded', function() {
    const carousel = document.getElementById('recomendados-carousel');
    const btnPrev = document.getElementById('recomendados-prev');
    const btnNext = document.getElementById('recomendados-next');
    if (!carousel || !btnPrev || !btnNext) return;
    const scrollAmount = 260; // px
    btnPrev.addEventListener('click', function() {
        carousel.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
    });
    btnNext.addEventListener('click', function() {
        carousel.scrollBy({ left: scrollAmount, behavior: 'smooth' });
    });
});
