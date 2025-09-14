// ----- Board & Canvas -----
const COLS = 10;
const ROWS = 20;

const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');
const scoreEl = document.getElementById('score');
const levelEl = document.getElementById('level');

let BLOCK_SIZE = 30;                 // will be updated on resize
let PLAY_WIDTH = COLS * BLOCK_SIZE;
let PLAY_HEIGHT = ROWS * BLOCK_SIZE;

function resizeCanvas() {
  // Keep 10:20 (1:2) aspect ratio and fit screen
  const controls = document.getElementById('controls');
  const controlsHeight = controls ? controls.offsetHeight : 0;
  const maxW = window.innerWidth;
  const maxH = window.innerHeight - controlsHeight;

  // determine block size that fits within viewport
  const maxPlayableWidth = Math.min(maxW, Math.floor(maxH / 2));
  BLOCK_SIZE = Math.floor(maxPlayableWidth / COLS);
  PLAY_WIDTH = COLS * BLOCK_SIZE;
  PLAY_HEIGHT = ROWS * BLOCK_SIZE;

  // match canvas display size
  canvas.style.width = PLAY_WIDTH + 'px';
  canvas.style.height = PLAY_HEIGHT + 'px';

  // set actual canvas resolution based on device pixel ratio
  const scale = window.devicePixelRatio || 1;
  canvas.width = PLAY_WIDTH * scale;
  canvas.height = PLAY_HEIGHT * scale;
  ctx.setTransform(scale, 0, 0, scale, 0, 0);
}
window.addEventListener('resize', resizeCanvas, { passive: true });
window.addEventListener('orientationchange', resizeCanvas, { passive: true });
resizeCanvas();

// ----- Shapes -----
const S = [
  ['.....','.....','..00.','.00..','.....'],
  ['.....','..0..','..00.','...0.','.....']
];
const Z = [
  ['.....','.....','.00..','..00.','.....'],
  ['.....','..0..','.00..','.0...','.....']
];
const I = [
  ['..0..','..0..','..0..','..0..','.....'],
  ['.....','0000.','.....','.....','.....']
];
const O = [['.....','.....','.00..','.00..','.....']];
const J = [
  ['.....','.0...','.000.','.....','.....'],
  ['.....','..00.','..0..','..0..','.....'],
  ['.....','.....','.000.','...0.','.....'],
  ['.....','..0..','..0..','.00..','.....']
];
const L = [
  ['.....','...0.','.000.','.....','.....'],
  ['.....','..0..','..0..','..00.','.....'],
  ['.....','.....','.000.','.0...','.....'],
  ['.....','.00..','..0..','..0..','.....']
];
const T = [
  ['.....','..0..','.000.','.....','.....'],
  ['.....','..0..','..00.','..0..','.....'],
  ['.....','.....','.000.','..0..','.....'],
  ['.....','..0..','.00..','..0..','.....']
];

const SHAPES = [S, Z, I, O, J, L, T];
const SHAPE_COLORS = ['#00ff00', '#ff0000', '#00ffff', '#ffff00', '#ffa500', '#0000ff', '#800080'];

// ----- Piece -----
class Piece {
  constructor(x, y, shape) {
    this.x = x;
    this.y = y;
    this.shape = shape;
    this.color = SHAPE_COLORS[SHAPES.indexOf(shape)];
    this.rotation = 0;
  }
}

function createGrid() {
  return Array.from({ length: ROWS }, () => Array(COLS).fill(0));
}

function convertShapeFormat(piece) {
  const positions = [];
  const format = piece.shape[piece.rotation % piece.shape.length];
  for (let i = 0; i < format.length; i++) {
    for (let j = 0; j < format[i].length; j++) {
      if (format[i][j] === '0') {
        positions.push({ x: piece.x + j - 2, y: piece.y + i - 4 });
      }
    }
  }
  return positions;
}

function validSpace(piece, grid) {
  const formatted = convertShapeFormat(piece);
  return formatted.every(p =>
    p.x >= 0 && p.x < COLS && p.y < ROWS && (p.y < 0 || grid[p.y][p.x] === 0)
  );
}

function getShape() {
  const shape = SHAPES[Math.floor(Math.random() * SHAPES.length)];
  return new Piece(5, 0, shape);
}

function clearRows(grid) {
  let rowsCleared = 0;
  for (let y = ROWS - 1; y >= 0; y--) {
    if (grid[y].every(cell => cell !== 0)) {
      grid.splice(y, 1);
      grid.unshift(Array(COLS).fill(0));
      rowsCleared++;
      y++; // re-check this index after unshift
    }
  }
  return rowsCleared;
}

// ----- Rendering -----
function drawBlock(color, x, y) {
  const px = x * BLOCK_SIZE;
  const py = y * BLOCK_SIZE;
  ctx.fillStyle = color;
  ctx.shadowColor = 'rgba(0,0,0,0.4)';
  ctx.shadowBlur = 4;
  ctx.fillRect(px, py, BLOCK_SIZE, BLOCK_SIZE);
  ctx.shadowColor = 'transparent';
  ctx.shadowBlur = 0;
  ctx.strokeStyle = '#222';
  ctx.strokeRect(px, py, BLOCK_SIZE, BLOCK_SIZE);
}

function drawGrid(grid) {
  for (let y = 0; y < grid.length; y++) {
    for (let x = 0; x < grid[y].length; x++) {
      const cell = grid[y][x];
      if (cell !== 0) {
        drawBlock(cell, x, y);
      } else {
        // grid lines
        ctx.strokeStyle = '#222';
        ctx.strokeRect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE);
      }
    }
  }
}

function draw() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  drawGrid(grid);
  const positions = convertShapeFormat(currentPiece);
  positions.forEach(pos => {
    if (pos.y >= 0) {
      drawBlock(currentPiece.color, pos.x, pos.y);
    }
  });
}

// ----- Game state -----
let grid = createGrid();
let currentPiece = getShape();
let nextPiece = getShape();
let dropCounter = 0;
let dropInterval = 500;
let lastTime = 0;
let score = 0;
let level = 1;
let linesCleared = 0;

function updateHUD() {
  scoreEl.textContent = 'Score: ' + score;
  levelEl.textContent = 'Level: ' + level;
}

updateHUD();

function lockPiece() {
  const positions = convertShapeFormat(currentPiece);
  positions.forEach(pos => {
    if (pos.y >= 0) grid[pos.y][pos.x] = currentPiece.color;
  });
  const cleared = clearRows(grid);
  if (cleared > 0) {
    score += cleared * 10;
    linesCleared += cleared;
    if (linesCleared >= level * 10) {
      level++;
      dropInterval = Math.max(100, 500 - (level - 1) * 50);
    }
  }
  currentPiece = nextPiece;
  nextPiece = getShape();
  if (!validSpace(currentPiece, grid)) {
    grid = createGrid();
    score = 0;
    level = 1;
    linesCleared = 0;
    dropInterval = 500;
  }
  updateHUD();
}

function update(time = 0) {
  const delta = time - lastTime;
  lastTime = time;
  dropCounter += delta;
  if (dropCounter > dropInterval) {
    currentPiece.y += 1;
    if (!validSpace(currentPiece, grid)) {
      currentPiece.y -= 1;
      lockPiece();
    }
    dropCounter = 0;
  }
  draw();
  requestAnimationFrame(update);
}

// ----- Controls (keyboard, buttons, touch) -----
function moveLeft() {
  currentPiece.x -= 1;
  if (!validSpace(currentPiece, grid)) currentPiece.x += 1;
}
function moveRight() {
  currentPiece.x += 1;
  if (!validSpace(currentPiece, grid)) currentPiece.x -= 1;
}
function softDrop() {
  currentPiece.y += 1;
  if (!validSpace(currentPiece, grid)) currentPiece.y -= 1;
}
function rotate() {
  currentPiece.rotation += 1;
  if (!validSpace(currentPiece, grid)) currentPiece.rotation -= 1;
}
function hardDrop() {
  do { currentPiece.y += 1; }
  while (validSpace(currentPiece, grid));
  currentPiece.y -= 1;
  lockPiece();
}

document.addEventListener('keydown', e => {
  e.preventDefault();
  if (e.key === 'ArrowLeft') moveLeft();
  else if (e.key === 'ArrowRight') moveRight();
  else if (e.key === 'ArrowDown') softDrop();
  else if (e.key === 'ArrowUp') rotate();
  else if (e.key === ' ') hardDrop();
});

const btnInstall = document.getElementById('install');

// Handle PWA installation
let deferredPrompt;
const isIOS = /iphone|ipad|ipod/i.test(window.navigator.userAgent);
if (isIOS) {
  btnInstall?.remove();
} else if (btnInstall) {
  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    btnInstall.style.display = 'inline-block';
  });

  btnInstall.addEventListener('click', () => {
    btnInstall.style.display = 'none';
    deferredPrompt.prompt();
    deferredPrompt = null;
  });
}

// Touch gestures on canvas
let startX = 0, startY = 0;
canvas.addEventListener('touchstart', (e) => {
  const t = e.touches[0];
  startX = t.clientX;
  startY = t.clientY;
}, { passive: true });

canvas.addEventListener('touchend', (e) => {
  const t = e.changedTouches[0];
  const dx = t.clientX - startX;
  const dy = t.clientY - startY;
  if (Math.abs(dx) > Math.abs(dy)) {
    if (dx > 30) moveRight();
    else if (dx < -30) moveLeft();
  } else {
    if (dy > 30) hardDrop();
    else if (dy < -30) rotate();
  }
}, { passive: true });

// ----- Start -----
update();
