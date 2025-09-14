// Starfield background animation
const starCanvas = document.getElementById('starfield');
const starCtx = starCanvas.getContext('2d');
let stars = [];
let STAR_WIDTH = 0;
let STAR_HEIGHT = 0;

function resizeStarfield() {
  STAR_WIDTH = window.innerWidth;
  STAR_HEIGHT = window.innerHeight;
  starCanvas.style.width = STAR_WIDTH + 'px';
  starCanvas.style.height = STAR_HEIGHT + 'px';
  const scale = window.devicePixelRatio || 1;
  starCanvas.width = STAR_WIDTH * scale;
  starCanvas.height = STAR_HEIGHT * scale;
  starCtx.setTransform(scale, 0, 0, scale, 0, 0);
  // regenerate stars to match new size
  const count = Math.floor(STAR_WIDTH * STAR_HEIGHT * 0.001);
  stars = Array.from({ length: count }, createStar);
}

function createStar() {
  return {
    x: Math.random() * STAR_WIDTH,
    y: Math.random() * STAR_HEIGHT,
    size: Math.random() * 2 + 0.5,
    speed: Math.random() * 40 + 20
  };
}

let lastTime = 0;
function step(time) {
  const delta = time - lastTime;
  lastTime = time;
  starCtx.clearRect(0, 0, STAR_WIDTH, STAR_HEIGHT);
  stars.forEach(star => {
    star.y += star.speed * (delta / 1000);
    if (star.y > STAR_HEIGHT) {
      star.x = Math.random() * STAR_WIDTH;
      star.y = 0;
    }
    starCtx.fillStyle = '#fff';
    starCtx.fillRect(star.x, star.y, star.size, star.size);
  });
  requestAnimationFrame(step);
}

window.addEventListener('resize', resizeStarfield, { passive: true });
window.addEventListener('orientationchange', resizeStarfield, { passive: true });
resizeStarfield();
requestAnimationFrame(step);
