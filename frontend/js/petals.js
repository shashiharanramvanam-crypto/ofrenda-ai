/**
 * Cempasúchil (Marigold) Petal & Copal Incense Smoke Engine
 * Renders organic, fluttering petals with wind drag and gentle rising incense smoke.
 */

(function () {
  const canvas = document.getElementById('petals-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  let width, height;
  function resize() {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
  }
  window.addEventListener('resize', resize);
  resize();

  // Petal Configuration
  const PETAL_COUNT = 38;
  const petals = [];
  const colors = [
    { main: '#ffa62b', edge: '#ff7b00' },
    { main: '#ffbe0b', edge: '#fb5607' },
    { main: '#ff9e00', edge: '#d90429' },
    { main: '#e85d04', edge: '#9d0208' }
  ];

  for (let i = 0; i < PETAL_COUNT; i++) {
    petals.push({
      x: Math.random() * width,
      y: Math.random() * height - height,
      size: 9 + Math.random() * 12,
      speedY: 0.8 + Math.random() * 1.5,
      speedX: -0.6 + Math.random() * 1.2,
      rotation: Math.random() * Math.PI * 2,
      rotSpeed: (Math.random() - 0.5) * 0.04,
      oscAmp: 25 + Math.random() * 35,
      oscSpeed: 0.015 + Math.random() * 0.02,
      color: colors[Math.floor(Math.random() * colors.length)],
      opacity: 0.65 + Math.random() * 0.35,
      tilt: Math.random() * Math.PI,
      tiltSpeed: 0.02 + Math.random() * 0.03
    });
  }

  let time = 0;

  function render() {
    ctx.clearRect(0, 0, width, height);
    time++;

    petals.forEach(p => {
      p.y += p.speedY;
      p.x += Math.sin(time * p.oscSpeed) * 0.8 + p.speedX;
      p.rotation += p.rotSpeed;
      p.tilt += p.tiltSpeed;

      // Wrap around edges
      if (p.y > height + 20) {
        p.y = -20;
        p.x = Math.random() * width;
      }
      if (p.x < -20) p.x = width + 20;
      if (p.x > width + 20) p.x = -20;

      // Draw 3D fluttering petal
      ctx.save();
      ctx.translate(p.x, p.y);
      ctx.rotate(p.rotation);
      ctx.scale(Math.cos(p.tilt), 1);

      // Petal shape
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.bezierCurveTo(-p.size / 2, -p.size, -p.size, p.size / 2, 0, p.size);
      ctx.bezierCurveTo(p.size, p.size / 2, p.size / 2, -p.size, 0, 0);
      ctx.closePath();

      const grad = ctx.createRadialGradient(0, p.size / 2, 2, 0, p.size / 2, p.size);
      grad.addColorStop(0, p.color.main);
      grad.addColorStop(1, p.color.edge);

      ctx.fillStyle = grad;
      ctx.globalAlpha = p.opacity;
      ctx.shadowColor = 'rgba(255, 170, 0, 0.4)';
      ctx.shadowBlur = 6;
      ctx.fill();

      ctx.restore();
    });

    requestAnimationFrame(render);
  }

  render();
})();
