import random
from typing import Dict, List, Tuple

# Grid dimensions
GRID_WIDTH = 10
GRID_HEIGHT = 20

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
SHAPE_COLORS = [(0, 255, 0), (255, 0, 0), (0, 255, 255),
                (255, 255, 0), (255, 165, 0), (0, 0, 255),
                (128, 0, 128)]


class Piece:
    def __init__(self, x: int, y: int, shape: List[List[str]]):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = SHAPE_COLORS[SHAPES.index(shape)]
        self.rotation = 0


def create_grid(locked_positions: Dict[Tuple[int, int], Tuple[int, int, int]]) -> List[List[Tuple[int, int, int]]]:
    grid = [[(0, 0, 0) for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    for (x, y), color in locked_positions.items():
        grid[y][x] = color
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
    accepted_positions = [(j, i) for i in range(GRID_HEIGHT) for j in range(GRID_WIDTH) if grid[i][j] == (0, 0, 0)]
    formatted = convert_shape_format(piece)
    return all(pos in accepted_positions and pos[1] > -1 for pos in formatted)


def move_piece(piece: Piece, dx: int, dy: int, grid: List[List[Tuple[int, int, int]]]) -> bool:
    piece.x += dx
    piece.y += dy
    if not valid_space(piece, grid):
        piece.x -= dx
        piece.y -= dy
        return False
    return True


def rotate_piece(piece: Piece, grid: List[List[Tuple[int, int, int]]]) -> bool:
    piece.rotation += 1
    if not valid_space(piece, grid):
        piece.rotation -= 1
        return False
    return True


def check_lost(positions: Dict[Tuple[int, int], Tuple[int, int, int]]) -> bool:
    return any(y < 1 for (_, y) in positions)


def get_shape() -> Piece:
    return Piece(5, 0, random.choice(SHAPES))


def clear_rows(grid: List[List[Tuple[int, int, int]]], locked: Dict[Tuple[int, int], Tuple[int, int, int]]) -> int:
    rows_to_clear = [i for i in range(len(grid) - 1, -1, -1) if (0, 0, 0) not in grid[i]]
    for row in rows_to_clear:
        for j in range(len(grid[row])):
            locked.pop((j, row), None)
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < row:
                locked[(x, y + 1)] = locked.pop(key)
    return len(rows_to_clear)


def lock_piece(piece: Piece, locked_positions: Dict[Tuple[int, int], Tuple[int, int, int]]) -> int:
    for pos in convert_shape_format(piece):
        locked_positions[(pos[0], pos[1])] = piece.color
    grid = create_grid(locked_positions)
    return clear_rows(grid, locked_positions) * 10
