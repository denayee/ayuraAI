// ==========================================
// static/js/landing.js
// Landing Page Animations & Interactivity
// ==========================================

document.addEventListener('DOMContentLoaded', () => {
    // Live Image Slider
    const slides = document.querySelectorAll('.banner-slide');
    let currentSlide = 0;
    if (slides.length > 0) {
        // Crossfade every 4 seconds
        setInterval(() => {
            slides[currentSlide].classList.remove('active');
            currentSlide = (currentSlide + 1) % slides.length;
            slides[currentSlide].classList.add('active');
        }, 4000); 
    }

    // Stacked Cards Advanced Scroll Animation
    const cards = document.querySelectorAll('.stacked-card');
    const stickyTop = window.innerHeight * 0.15; // 15vh

    // 1. Initial Reveal via Intersection Observer
    const observerElements = document.querySelectorAll('.stacked-card, .how-card, .reveal-up');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
            }
        });
    }, { threshold: 0.1 });

    observerElements.forEach(el => observer.observe(el));

    // Stacked card continuous scroll effect was removed as cards are now in a grid layout.

    // Live Number Counting Animation
    const statNumbers = document.querySelectorAll('.stat-number');
    let hasCounted = false;

    const countObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !hasCounted) {
                hasCounted = true; 
                
                statNumbers.forEach(stat => {
                    const target = +stat.getAttribute('data-target');
                    const increment = target / 60; 
                    let current = 0;

                    const updateCount = () => {
                        current += increment;
                        if (current < target) {
                            stat.innerText = Math.ceil(current).toLocaleString();
                            requestAnimationFrame(updateCount);
                        } else {
                            stat.innerText = target.toLocaleString();
                        }
                    };
                    updateCount();
                });
            }
        });
    }, { threshold: 0.5 }); 

    const statsSection = document.querySelector('.stats-section');
    if (statsSection) {
        countObserver.observe(statsSection);
    }
});
