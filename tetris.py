import pygame
import random
import math
from typing import List, Tuple

# Initialize pygame's font module
pygame.font.init()

# Game dimensions
S_WIDTH = 800
S_HEIGHT = 750
PLAY_WIDTH = 150  # 10 blocks wide
PLAY_HEIGHT = 300  # 20 blocks high

# logical grid dimensions
COLS = 10
ROWS = 20

# derive cell spacing from the fixed board size
CELL_STEP = min(PLAY_WIDTH // COLS, PLAY_HEIGHT // ROWS)
# visual cell is half the logical step
CELL_SIZE = CELL_STEP // 2
# center smaller cells within each logical step
CELL_OFFSET = (CELL_STEP - CELL_SIZE) // 2

TOP_LEFT_X = (S_WIDTH - PLAY_WIDTH) // 2
TOP_LEFT_Y = S_HEIGHT - PLAY_HEIGHT - 50

# Shapes represented in a 5x5 grid
S = [['.....',
      '.....',
      '..00.',
      '.00..',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '...0.',
      '.....']]

Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.0...',
      '.....']]

I = [['..0..',
      '..0..',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '0000.',
      '.....',
      '.....',
      '.....']]

O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]

J = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '.....']]

L = [['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '.....']]

T = [['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]

SHAPES = [S, Z, I, O, J, L, T]

# Base colors for the original theme
SHAPE_COLORS = [
    (0, 255, 0),
    (255, 0, 0),
    (0, 255, 255),
    (255, 255, 0),
    (255, 165, 0),
    (0, 0, 255),
    (128, 0, 128),
]

# Additional color themes mapped by name
THEME_COLORS = {
    'classic': SHAPE_COLORS,
    'neon': [
        (57, 255, 20),
        (255, 20, 147),
        (0, 255, 255),
        (255, 255, 0),
        (255, 127, 80),
        (0, 191, 255),
        (186, 85, 211),
    ],
    'pastel': [
        (119, 221, 119),
        (255, 179, 186),
        (186, 225, 255),
        (255, 255, 204),
        (253, 253, 150),
        (202, 231, 255),
        (221, 160, 221),
    ],
}

theme_names = list(THEME_COLORS.keys())
current_theme_index = 0
current_theme = theme_names[current_theme_index]


def get_color(index: int) -> Tuple[int, int, int]:
    return THEME_COLORS[current_theme][index]


class Piece:
    def __init__(self, x: int, y: int, shape: List[List[str]]):
        self.x = x
        self.y = y
        self.shape = shape
        self.color_index = SHAPES.index(shape)
        self.rotation = 0

    @property
    def color(self) -> Tuple[int, int, int]:
        return get_color(self.color_index)


def create_grid(locked_positions: dict) -> List[List[Tuple[int, int, int]]]:
    grid = [[(0, 0, 0) for _ in range(COLS)] for _ in range(ROWS)]
    for (j, i), color_idx in locked_positions.items():
        if 0 <= i < ROWS and 0 <= j < COLS:
            grid[i][j] = get_color(color_idx)
    return grid


def convert_shape_format(piece: Piece) -> List[Tuple[int, int]]:
    positions = []
    format = piece.shape[piece.rotation % len(piece.shape)]
    for i, line in enumerate(format):
        for j, char in enumerate(line):
            if char == '0':
                positions.append((piece.x + j - 2, piece.y + i - 4))
    return positions


def valid_space(piece: Piece, grid: List[List[Tuple[int, int, int]]]) -> bool:
    accepted_positions = [(j, i) for i in range(ROWS) for j in range(COLS) if grid[i][j] == (0, 0, 0)]
    formatted = convert_shape_format(piece)
    for x, y in formatted:
        if (x, y) not in accepted_positions and y > -1:
            return False
    return True


def check_lost(positions: dict) -> bool:
    return any(y < 1 for (_, y) in positions)


def get_shape() -> Piece:
    return Piece(COLS // 2, 0, random.choice(SHAPES))


# ---- Minimal inline game logic to replace missing imports ----

def move_piece(piece: Piece, dx: int, dy: int, grid) -> bool:
    old_x, old_y = piece.x, piece.y
    piece.x += dx
    piece.y += dy
    if not valid_space(piece, grid):
        piece.x, piece.y = old_x, old_y
        return False
    return True


def rotate_piece(piece: Piece, grid) -> None:
    old_rot = piece.rotation
    piece.rotation = (piece.rotation + 1) % len(piece.shape)
    if not valid_space(piece, grid):
        piece.rotation = old_rot


def clear_rows(locked: dict) -> int:
    """Remove full rows from locked positions; return number of cleared rows."""
    rows_to_clear = []
    for i in range(ROWS):
        if all((j, i) in locked for j in range(COLS)):
            rows_to_clear.append(i)
    if not rows_to_clear:
        return 0

    # Remove cleared rows
    for i in rows_to_clear:
        for j in range(COLS):
            locked.pop((j, i), None)

    # Shift everything above down
    rows_to_clear = sorted(rows_to_clear)
    for (x, y) in sorted(list(locked.keys()), key=lambda p: p[1], reverse=True):
        shift = sum(1 for r in rows_to_clear if y < r)
        if shift:
            locked[(x, y + shift)] = locked.pop((x, y))
    return len(rows_to_clear)


def lock_piece(piece: Piece, locked_positions: dict) -> int:
    for (x, y) in convert_shape_format(piece):
        locked_positions[(x, y)] = piece.color_index
    cleared = clear_rows(locked_positions)
    # simple scoring: 100 points per cleared row
    return cleared * 100
# --------------------------------------------------------------


def draw_text_middle(surface, text, size, color):
    font = pygame.font.SysFont('comicsans', size, bold=True)
    label = font.render(text, True, color)
    surface.blit(label, (TOP_LEFT_X + PLAY_WIDTH / 2 - label.get_width() / 2,
                         TOP_LEFT_Y + PLAY_HEIGHT / 2 - label.get_height() / 2))


def draw_grid(surface, grid):
    for i in range(len(grid)):
        y = TOP_LEFT_Y + i * CELL_STEP
        pygame.draw.line(surface, (128, 128, 128), (TOP_LEFT_X, y),
                         (TOP_LEFT_X + PLAY_WIDTH, y))
    for j in range(len(grid[0])):
        x = TOP_LEFT_X + j * CELL_STEP
        pygame.draw.line(surface, (128, 128, 128), (x, TOP_LEFT_Y),
                         (x, TOP_LEFT_Y + PLAY_HEIGHT))


def draw_next_shape(shape, surface):
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Next Shape', True, (255, 255, 255))
    sx = TOP_LEFT_X + PLAY_WIDTH + 50
    sy = TOP_LEFT_Y + PLAY_HEIGHT / 2 - 100
    format = shape.shape[shape.rotation % len(shape.shape)]
    for i, line in enumerate(format):
        for j, char in enumerate(line):
            if char == '0':
                pygame.draw.rect(surface, shape.color,
                                 (sx + j * CELL_SIZE, sy + i * CELL_SIZE, CELL_SIZE, CELL_SIZE), 0)
    surface.blit(label, (sx + 10, sy - 30))


def draw_background(surface, tick):
    for y in range(S_HEIGHT):
        offset = (y + tick * 0.02)
        color = (
            20 + int(20 * math.sin(offset)),
            20 + int(20 * math.sin(offset + 2)),
            20 + int(20 * math.sin(offset + 4)),
        )
        pygame.draw.line(surface, color, (0, y), (S_WIDTH, y))


def draw_window(surface, grid, score=0):
    tick = pygame.time.get_ticks()
    draw_background(surface, tick)
    font = pygame.font.SysFont('comicsans', 60)
    label = font.render('Tetris', True, (255, 255, 255))
    surface.blit(label, (TOP_LEFT_X + PLAY_WIDTH / 2 - label.get_width() / 2, 30))
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Score: ' + str(score), True, (255, 255, 255))
    sx = TOP_LEFT_X + PLAY_WIDTH + 50
    sy = TOP_LEFT_Y + PLAY_HEIGHT / 2 - 100
    surface.blit(label, (sx + 20, sy + 160))
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            x = TOP_LEFT_X + j * CELL_STEP + CELL_OFFSET
            y = TOP_LEFT_Y + i * CELL_STEP + CELL_OFFSET
            pygame.draw.rect(surface, grid[i][j],
                             (x, y, CELL_SIZE, CELL_SIZE), 0)
    draw_grid(surface, grid)
    pygame.draw.rect(surface, (255, 0, 0),
                     (TOP_LEFT_X, TOP_LEFT_Y, PLAY_WIDTH, PLAY_HEIGHT), 5)


def main():
    global current_theme_index, current_theme
    locked_positions = {}
    grid = create_grid(locked_positions)
    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.5
    level_time = 0
    score = 0
    screen = pygame.display.set_mode((S_WIDTH, S_HEIGHT))
    pygame.display.set_caption('Tetris')

    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        level_time += clock.get_rawtime()
        clock.tick()

        if level_time / 1000 > 5:
            level_time = 0
            if fall_speed > 0.12:
                fall_speed -= 0.005

        if fall_time / 1000 > fall_speed:
            fall_time = 0
            if not move_piece(current_piece, 0, 1, grid):
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    move_piece(current_piece, -1, 0, grid)
                elif event.key == pygame.K_RIGHT:
                    move_piece(current_piece, 1, 0, grid)
                elif event.key == pygame.K_DOWN:
                    move_piece(current_piece, 0, 1, grid)
                elif event.key == pygame.K_UP:
                    rotate_piece(current_piece, grid)
                elif event.key == pygame.K_t:
                    current_theme_index = (current_theme_index + 1) % len(theme_names)
                    current_theme = theme_names[current_theme_index]

        shape_pos = convert_shape_format(current_piece)
        for j, i in shape_pos:
            if i > -1:
                grid[i][j] = current_piece.color

        if change_piece:
            score += lock_piece(current_piece, locked_positions)
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False

        draw_window(screen, grid, score)
        draw_next_shape(next_piece, screen)
        pygame.display.update()

        if check_lost(locked_positions):
            draw_text_middle(screen, 'You Lost', 80, (255, 255, 255))
            pygame.display.update()
            pygame.time.delay(1500)
            run = False


def main_menu():
    screen = pygame.display.set_mode((S_WIDTH, S_HEIGHT))
    run = True
    while run:
        screen.fill((0, 0, 0))
        draw_text_middle(screen, 'Press any key to play', 60, (255, 255, 255))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                main()
    pygame.quit()


if __name__ == '__main__':
    main_menu()
