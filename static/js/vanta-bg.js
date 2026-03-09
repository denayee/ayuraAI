// Initialize Vanta NET on the hero container to act as a poster-style background
if (typeof VANTA !== 'undefined' && VANTA.NET) {
  VANTA.NET({
    el: "#vanta-poster",
    mouseControls: true,
    touchControls: true,
    gyroControls: false,
    minHeight: 200.00,
    minWidth: 200.00,
    scale: 1.00,
    scaleMobile: 1.00,
    backgroundColor: 0x0f172a,
    color: 0x2ecc71,
    points: 8.00,
    maxDistance: 20.00,
    spacing: 15.00
  });
}