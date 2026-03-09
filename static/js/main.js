// ==========================================
// static/js/main.js
// Global UI Scripts (Theme, Navbar, Flash JS)
// ==========================================

document.addEventListener('DOMContentLoaded', () => {
    // ——— Theme ———
    function applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        const icon = theme === 'dark' ? '☀️' : '🌙';
        document.querySelectorAll('.theme-toggle-btn').forEach(b => b.textContent = icon);
    }
    
    const savedTheme = localStorage.getItem('theme') || 'light';
    applyTheme(savedTheme);

    document.querySelectorAll('.theme-toggle-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const curr = document.documentElement.getAttribute('data-theme');
            const next = curr === 'dark' ? 'light' : 'dark';
            localStorage.setItem('theme', next);
            applyTheme(next);
        });
    });

    // ——— Hamburger Navbar ———
    const hamburgerBtn = document.getElementById('hamburgerBtn');
    const mobileNav = document.getElementById('mobileNav');

    if (hamburgerBtn && mobileNav) {
        hamburgerBtn.addEventListener('click', () => {
            const isOpen = mobileNav.classList.toggle('mobile-nav-open');
            hamburgerBtn.classList.toggle('is-active', isOpen);
            document.body.style.overflow = isOpen ? 'hidden' : '';
        });

        // Close mobile nav when any link inside it is clicked
        mobileNav.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                mobileNav.classList.remove('mobile-nav-open');
                hamburgerBtn.classList.remove('is-active');
                document.body.style.overflow = '';
            });
        });
    }

    // ——— Flash messages auto-dismiss ———
    const flashMessages = document.querySelectorAll('.flash-message');
    if (flashMessages.length > 0) {
        flashMessages.forEach(msg => {
            setTimeout(() => {
                msg.classList.add('fade-out');
                setTimeout(() => msg.remove(), 400);
            }, 1500);
        });
    }
});
