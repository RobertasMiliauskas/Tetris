const canvas = document.getElementById('tetris');
const context = canvas.getContext('2d');

function resizeCanvas() {
  // Maintain 10:20 (1:2) aspect ratio
  const maxWidth = window.innerWidth;
  const maxHeight = window.innerHeight;
  let width = Math.min(maxWidth, maxHeight / 2);
  let height = width * 2;
  canvas.width = width;
  canvas.height = height;
}

window.addEventListener('resize', resizeCanvas);
window.addEventListener('orientationchange', resizeCanvas);
resizeCanvas();

// Placeholder game state
function draw() {
  context.fillStyle = '#000';
  context.fillRect(0, 0, canvas.width, canvas.height);
  // draw grid for visibility
  context.strokeStyle = '#222';
  const cellWidth = canvas.width / 10;
  const cellHeight = canvas.height / 20;
  for (let x = 0; x <= canvas.width; x += cellWidth) {
    context.beginPath();
    context.moveTo(x, 0);
    context.lineTo(x, canvas.height);
    context.stroke();
  }
  for (let y = 0; y <= canvas.height; y += cellHeight) {
    context.beginPath();
    context.moveTo(0, y);
    context.lineTo(canvas.width, y);
    context.stroke();
  }
}

draw();

function moveLeft() { console.log('move left'); }
function moveRight() { console.log('move right'); }
function rotate() { console.log('rotate'); }
function drop() { console.log('drop'); }

document.getElementById('left').addEventListener('click', moveLeft);
document.getElementById('right').addEventListener('click', moveRight);
document.getElementById('rotate').addEventListener('click', rotate);
document.getElementById('drop').addEventListener('click', drop);

let startX = 0;
let startY = 0;
canvas.addEventListener('touchstart', (e) => {
  const touch = e.touches[0];
  startX = touch.clientX;
  startY = touch.clientY;
}, {passive: true});

canvas.addEventListener('touchend', (e) => {
  const touch = e.changedTouches[0];
  const dx = touch.clientX - startX;
  const dy = touch.clientY - startY;
  if (Math.abs(dx) > Math.abs(dy)) {
    if (dx > 30) moveRight();
    else if (dx < -30) moveLeft();
  } else {
    if (dy > 30) drop();
    else if (dy < -30) rotate();
  }
}, {passive: true});
