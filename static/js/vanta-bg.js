// Initialize Vanta Globe on the hero container
function setVanta() {
  try {
    if (typeof VANTA === 'undefined' || !VANTA.GLOBE) return;
    if (window.vantaEffect) {
      window.vantaEffect.destroy()
      window.vantaEffect = null
    }
    
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const bgColor = isDark ? 0x0f172a : 0xffffff; // slate 900 for dark mode, white for light
    const primaryColor = isDark ? 0x14b8a6 : 0x0d9488; // primary color
    
    window.vantaEffect = VANTA.GLOBE({
      el: "#vanta-poster",
      mouseControls: true,
      touchControls: true,
      gyroControls: false,
      minHeight: 200.00,
      minWidth: 200.00,
      scale: 1.00,
      scaleMobile: 1.00,
      color: primaryColor,
      color2: isDark ? 0xffffff : 0x000000,
      backgroundColor: bgColor
    })
  } catch (e) {
    console.warn('Vanta init failed', e)
  }
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', setVanta)
} else {
  setVanta()
}

// Watch for theme changes so the background updates dynamically
const themeObserver = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
        if (mutation.attributeName === 'data-theme') {
            setVanta();
        }
    });
});

themeObserver.observe(document.documentElement, { attributes: true });

if (window._strk && typeof _strk.push === 'function') {
  _strk.push(function() {
    setVanta()
    if (window.edit_page && edit_page.Event && typeof edit_page.Event.subscribe === 'function') {
      window.edit_page.Event.subscribe("Page.beforeNewOneFadeIn", setVanta)
    }
  })
}