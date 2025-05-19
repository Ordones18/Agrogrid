document.addEventListener('DOMContentLoaded', function() {
    const toggle = document.querySelector('.mobile-menu-toggle');
    const nav = document.querySelector('.navigation');
    toggle.addEventListener('click', function() {
        nav.classList.toggle('active');
    });
});