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

    // Continuous Scroll Effect for "Fading Behind" Stack Panels
    window.addEventListener('scroll', () => {
        cards.forEach((card, index) => {
            if (!card.classList.contains('is-visible')) return;
            
            const rect = card.getBoundingClientRect();
            
            if (rect.top <= stickyTop + 10) { 
                if (index < cards.length - 1) {
                    const nextCard = cards[index + 1];
                    const nextRect = nextCard.getBoundingClientRect();
                    const distanceToNext = nextRect.top - stickyTop;
                    const fadeStartDistance = window.innerHeight * 0.55; 
                    
                    if (distanceToNext < fadeStartDistance && distanceToNext > 0) {
                        const progress = 1 - (distanceToNext / fadeStartDistance); 
                        const scale = 1 - (progress * 0.05);
                        const yOffset = -(progress * 40);
                        
                        card.style.transform = `scale(${scale}) translateY(${yOffset}px)`;
                        card.style.opacity = 1 - (progress * 0.6); 
                    } else if (distanceToNext <= 0) {
                        card.style.transform = `scale(0.95) translateY(-40px)`;
                        card.style.opacity = 0.4;
                    } else {
                        card.style.transform = '';
                        card.style.opacity = '';
                    }
                }
            } else {
                card.style.transform = '';
                card.style.opacity = '';
            }
        });
    });

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
