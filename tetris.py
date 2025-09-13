import pygame
import random
import math
from typing import List, Tuple

# Initialize pygame's font module
pygame.font.init()

# Game dimensions
S_WIDTH = 800
S_HEIGHT = 750
PLAY_WIDTH = 300  # 10 blocks wide
PLAY_HEIGHT = 600  # 20 blocks high
BLOCK_SIZE = 30

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

# Color themes for pieces
SHAPE_COLORS = {
    'classic': [(0, 255, 0), (255, 0, 0), (0, 255, 255),
                (255, 255, 0), (255, 165, 0), (0, 0, 255),
                (128, 0, 128)],
    'neon': [(57, 255, 20), (255, 20, 147), (0, 255, 255),
             (255, 255, 0), (255, 127, 80), (0, 191, 255),
             (186, 85, 211)],
    'pastel': [(119, 221, 119), (255, 179, 186), (186, 225, 255),
               (255, 255, 204), (253, 253, 150), (202, 231, 255),
               (221, 160, 221)]
}

theme_names = list(SHAPE_COLORS.keys())
current_theme_index = 0
current_theme = theme_names[current_theme_index]


def get_color(index: int) -> Tuple[int, int, int]:
    return SHAPE_COLORS[current_theme][index]

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
    grid = [[(0, 0, 0) for _ in range(10)] for _ in range(20)]
    for (j, i), color_idx in locked_positions.items():
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
    accepted_positions = [(j, i) for i in range(20) for j in range(10) if grid[i][j] == (0, 0, 0)]
    formatted = convert_shape_format(piece)
    return all(pos in accepted_positions and pos[1] > -1 for pos in formatted)


def check_lost(positions: dict) -> bool:
    return any(y < 1 for (_, y) in positions)


def get_shape() -> Piece:
    return Piece(5, 0, random.choice(SHAPES))


def draw_text_middle(surface, text, size, color):
    font = pygame.font.SysFont('comicsans', size, bold=True)
    label = font.render(text, True, color)
    surface.blit(label, (TOP_LEFT_X + PLAY_WIDTH / 2 - label.get_width() / 2,
                         TOP_LEFT_Y + PLAY_HEIGHT / 2 - label.get_height() / 2))


def draw_grid(surface, grid):
    for i in range(len(grid)):
        pygame.draw.line(surface, (128, 128, 128), (TOP_LEFT_X, TOP_LEFT_Y + i * BLOCK_SIZE),
                         (TOP_LEFT_X + PLAY_WIDTH, TOP_LEFT_Y + i * BLOCK_SIZE))
        for j in range(len(grid[i])):
            pygame.draw.line(surface, (128, 128, 128), (TOP_LEFT_X + j * BLOCK_SIZE, TOP_LEFT_Y),
                             (TOP_LEFT_X + j * BLOCK_SIZE, TOP_LEFT_Y + PLAY_HEIGHT))


def clear_rows(grid, locked):
    rows_to_clear = [i for i in range(len(grid) - 1, -1, -1) if (0, 0, 0) not in grid[i]]
    for row in rows_to_clear:
        del_row = row
        for j in range(len(grid[row])):
            try:
                del locked[(j, row)]
            except KeyError:
                pass
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < del_row:
                locked[(x, y + 1)] = locked.pop(key)
    return len(rows_to_clear)


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
                                 (sx + j * BLOCK_SIZE, sy + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)
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
            pygame.draw.rect(surface, grid[i][j],
                             (TOP_LEFT_X + j * BLOCK_SIZE, TOP_LEFT_Y + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)
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
            current_piece.y += 1
            if not valid_space(current_piece, grid) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1
                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                elif event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1
                elif event.key == pygame.K_UP:
                    current_piece.rotation += 1
                    if not valid_space(current_piece, grid):
                        current_piece.rotation -= 1
                elif event.key == pygame.K_t:
                    current_theme_index = (current_theme_index + 1) % len(theme_names)
                    current_theme = theme_names[current_theme_index]
        shape_pos = convert_shape_format(current_piece)
        for j, i in shape_pos:
            if i > -1:
                grid[i][j] = current_piece.color
        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color_index
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            score += clear_rows(grid, locked_positions) * 10
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
