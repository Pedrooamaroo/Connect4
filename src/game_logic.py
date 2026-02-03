import numpy as np

ROW_COUNT = 6
COLUMN_COUNT = 7
WIN_X = 512
WIN_O = -512
SEGMENT_VALUES_O = {0: 0, 1: -1, 2: -10, 3: -50}
SEGMENT_VALUES_X = {0: 0, 1: 1, 2: 10, 3: 50}
MOVE_BONUS_X = 16
MOVE_BONUS_O = -16

def create_board():
    return [[0 for _ in range(7)] for _ in range(6)]

def is_empty(board, col):
    return board[5][col] == 0

def check_next_empty_row(board, col):
    for r in range(6):
        if board[r][col] == 0:
            return r

def put_piece(board, row, col, piece):
    board[row][col] = piece

def get_valid_locations(board):
    res = []
    for i in range(7):
        if is_empty(board, i):
            res.append(i)
    return res

def win(piece, board):

    for c in range(4):
        for r in range(6):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                return True

    for c in range(7):
        for r in range(3):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                return True

    for c in range(4):
        for r in range(3):
            if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                return True

    for c in range(4):
        for r in range(3, 6):
            if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                return True
    return False

def draw(board):
    if win(1, board) or win(2, board):
        return False
    for i in range(6):
        for j in range(7):
            if board[i][j] == 0:
                return False
    return True