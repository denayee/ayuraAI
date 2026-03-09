// Initialize Vanta Globe on the hero container
function setVanta() {
  try {
    if (typeof VANTA === 'undefined' || !VANTA.GLOBE) return;
    if (window.vantaEffect) {
      window.vantaEffect.destroy()
      window.vantaEffect = null
    }
    window.vantaEffect = VANTA.GLOBE({
      el: "#vanta-poster",
      mouseControls: true,
      touchControls: true,
      gyroControls: false,
      minHeight: 200.00,
      minWidth: 200.00,
      scale: 1.00,
      scaleMobile: 1.00,
      color: 0x3fff82,
      color2: 0x0,
      backgroundColor: 0xffffff
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

if (window._strk && typeof _strk.push === 'function') {
  _strk.push(function() {
    setVanta()
    if (window.edit_page && edit_page.Event && typeof edit_page.Event.subscribe === 'function') {
      window.edit_page.Event.subscribe("Page.beforeNewOneFadeIn", setVanta)
    }
  })
}