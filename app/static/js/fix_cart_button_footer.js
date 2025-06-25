// Este script se encarga de ajustar la posición del botón flotante para que nunca tape el footer y siempre sea visible
document.addEventListener('DOMContentLoaded', function() {
    const cartBtn = document.querySelector('.btn-float-cart');
    const footer = document.querySelector('footer, .footer, .site-footer');
    if (!cartBtn || !footer) return;

    function adjustCartBtn() {
        const footerRect = footer.getBoundingClientRect();
        const windowHeight = window.innerHeight;
        const overlap = windowHeight - footerRect.top;
        if (overlap > 0) {
            cartBtn.style.bottom = (overlap + 32) + 'px';
        } else {
            cartBtn.style.bottom = '32px';
        }
    }

    window.addEventListener('scroll', adjustCartBtn);
    window.addEventListener('resize', adjustCartBtn);
    adjustCartBtn();
});
