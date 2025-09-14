import os
import sys

import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from game_logic import (
    O,
    SHAPES,
    Piece,
    check_lost,
    create_grid,
    lock_piece,
    move_piece,
)


def test_move_piece_bounds():
    grid = create_grid({})
    piece = Piece(5, 2, SHAPES[0])
    assert move_piece(piece, -1, 0, grid)
    assert piece.x == 4
    assert not move_piece(piece, -5, 0, grid)
    assert piece.x == 4


def test_lock_piece_and_score():
    locked = {(i, 19): (255, 255, 255) for i in range(2, 10)}
    piece = Piece(1, 20, O)
    score = lock_piece(piece, locked)
    assert score == 10
    grid = create_grid(locked)
    assert sum(1 for cell in grid[19] if cell != (0, 0, 0)) == 2
    assert all((0, 0, 0) in row for row in grid)


def test_check_lost():
    locked = {(0, 0): (255, 255, 255)}
    assert check_lost(locked)
