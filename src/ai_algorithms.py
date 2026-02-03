import math
import copy
import random
import time
import numpy as np
import pandas as pd
from collections import Counter
from game_logic import (
    is_empty, check_next_empty_row, put_piece, win, draw, 
    get_valid_locations, ROW_COUNT, COLUMN_COUNT, WIN_X, WIN_O,
    SEGMENT_VALUES_O, SEGMENT_VALUES_X, MOVE_BONUS_X, MOVE_BONUS_O
)

# Helper methods

def evaluate_window(window, piece):
    score = 0
    opponent_piece = 1 if piece == 2 else 2

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(0) == 1:
        score += 10
    elif window.count(piece) == 2 and window.count(0) == 2:
        score += 5

    if window.count(opponent_piece) == 3 and window.count(0) == 1:
        score -= 80  

    return score

def evaluate_board(board, piece=2):
    score = 0


    center_col = [board[i][3] for i in range(6)]
    center_score = center_col.count(piece)
    score += center_score * 6

    for row in board:
        for c in range(4):
            window = row[c:c+4]
            score += evaluate_window(window, piece)

    for c in range(7):
        col_array = [board[r][c] for r in range(6)]
        for r in range(3):
            window = col_array[r:r+4]
            score += evaluate_window(window, piece)

    for r in range(3):
        for c in range(4):
            window = [board[r+i][c+i] for i in range(4)]
            score += evaluate_window(window, piece)

    for r in range(3):
        for c in range(4):
            window = [board[r+3-i][c+i] for i in range(4)]
            score += evaluate_window(window, piece)

    return score

def score_position(board, piece):
    score = 0
    WINDOW_LENGTH = 4
    
    # Score center column
    center_array = [board[i][3] for i in range(6)]
    center_count = center_array.count(piece)
    score += center_count * 6

    # Score Horizontal
    for r in range(ROW_COUNT):
        row_array = board[r]
        for c in range(COLUMN_COUNT-3):
            window = row_array[c:c+WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # Score Vertical
    for c in range(COLUMN_COUNT):
        col_array = [board[i][c] for i in range(6)]
        for r in range(ROW_COUNT-3):
            window = col_array[r:r+WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # Score positive sloped diagonal
    for r in range(ROW_COUNT-3):
        for c in range(COLUMN_COUNT-3):
            window = [board[r+i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    # Score negative sloped diagonal
    for r in range(ROW_COUNT-3):
        for c in range(COLUMN_COUNT-3):
            window = [board[r+3-i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    return score

# A*


def a_star(board):
    best_move = None
    best_score = -512

    for column in range(0, 7):
        if is_empty(board, column):
            row = check_next_empty_row(board, column)
            new_board = copy.deepcopy(board)
            new_board[row][column] = 2
            score = evaluate_board(new_board)
            if score > best_score:
                best_score = score
                best_move = column
    return best_move

def a_star_with_level(board, level):
    best_move = None
    best_score = -float('inf')

    for column in range(7):
        if is_empty(board, column):
            row = check_next_empty_row(board, column)
            new_board = copy.deepcopy(board)
            new_board[row][column] = 2
            score = evaluate_board(new_board) + (level * 10)

            if score > best_score:
                best_score = score
                best_move = column

    return best_move

# MiniMax

def minimax(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_locations(board)
    is_terminal = win(1, board) or win(2, board) or draw(board)
    
    if depth == 0 or is_terminal:
        if is_terminal:
            if win(2, board):
                return (None, 100000000000000)
            elif win(1, board):
                return (None, -10000000000000)
            else:
                return (None, 0)
        else:
            return (None, score_position(board, 2))
            
    if maximizingPlayer:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = check_next_empty_row(board, col)
            b_copy = copy.deepcopy(board)
            put_piece(b_copy, row, col, 2)
            new_score = minimax(b_copy, depth-1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value

    else:
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = check_next_empty_row(board, col)
            b_copy = copy.deepcopy(board)
            put_piece(b_copy, row, col, 1)
            new_score = minimax(b_copy, depth-1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value

# MCTS

class MCTSNode:
    def __init__(self, board, move=None, parent=None, player_num=1):
        self.board = board
        self.move = move
        self.parent = parent
        self.children = {}
        self.wins = 0
        self.visits = 0
        self.untried_moves = [col for col in range(7) if is_empty(board, col)]
        self.player_num = player_num

    def UCB1(self, total_visits, C=2):
        if self.visits == 0:
            return float('inf')
        win_rate = self.wins / self.visits
        exploration_factor = C * math.sqrt((math.log(total_visits)) / self.visits)
        return win_rate + exploration_factor

    def select_child(self):
        return max(self.children.values(), key=lambda child: child.UCB1(self.visits))

    def add_child(self, move, player_num):
        new_board = np.copy(self.board)
        row = check_next_empty_row(new_board, move)
        put_piece(new_board, row, move, player_num)
        child_node = MCTSNode(new_board, move=move, parent=self, player_num=3 - player_num)
        self.untried_moves.remove(move)
        self.children[move] = child_node
        return child_node

    def update(self, result):
        self.visits += 1
        if result == self.player_num:
            self.wins += 1
        elif result != 0:
            self.wins -= 1

def simulate(board, player_num):
    temp_board = np.copy(board)
    current_player = player_num

    while True:
        moves = [col for col in range(7) if is_empty(temp_board, col)]
        if not moves:
            return 0

        move = random.choice(moves)
        row = check_next_empty_row(temp_board, move)
        put_piece(temp_board, row, move, current_player)

        if win(current_player, temp_board):
            return current_player

        current_player = 3 - current_player

def MCTS(root, time_limit=1):
    start_time = time.time()
    while (time.time() - start_time) < time_limit:
        node = root

        # Selection
        while node.untried_moves == [] and node.children:
            node = node.select_child()

        # Expansion
        if node.untried_moves:
            move = random.choice(node.untried_moves)
            node = node.add_child(move, node.player_num)

        # Simulation
        current_result = simulate(node.board, node.player_num)

        # Backpropagation
        while node is not None:
            node.update(current_result)
            node = node.parent

def monte_carlo(board, player_num=1, time_limit=1):
    root = MCTSNode(np.copy(board), move=None, parent=None, player_num=player_num)
    MCTS(root, time_limit)
    valid_children = [child for child in root.children.values() if child.visits > 0]
    if not valid_children:
        valid_moves = [col for col in range(7) if is_empty(board, col)]
        return random.choice(valid_moves) if valid_moves else None
    
    best_move = max(valid_children, key=lambda x: (x.visits, -abs(x.move - 3))).move
    return best_move

def monte_carlo_difficulty(board, player_num=1, simulations=100):
    root = MCTSNode(np.copy(board), move=None, parent=None, player_num=player_num)
    simulations_done = 0

    while simulations_done < simulations:
        node = root

        while node.children and not node.untried_moves:
            node = node.select_child()

        if node.untried_moves:
            move = random.choice(node.untried_moves)
            node = node.add_child(move, node.player_num)

        result = simulate(node.board, node.player_num)

        while node is not None:
            node.update(result)
            node = node.parent

        simulations_done += 1

    valid_children = [child for child in root.children.values() if child.visits > 0]
    if not valid_children:
        valid_moves = [col for col in range(7) if is_empty(board, col)]
        return random.choice(valid_moves) if valid_moves else None

    best_move = max(valid_children, key=lambda x: (x.visits, -abs(x.move - 3))).move
    return best_move

# ID3 Decision Tree

def calcular_entropia(coluna):
    total = len(coluna)
    contador = Counter(coluna)
    entropia = 0
    for classe in contador:
        prob = contador[classe] / total
        entropia -= prob * math.log2(prob)
    return entropia

def ganho_informacao(df, atributo, alvo):
    entropia_total = calcular_entropia(df[alvo])
    valores_unicos = df[atributo].unique()
    entropia_atributo = 0

    for valor in valores_unicos:
        subconjunto = df[df[atributo] == valor]
        peso = len(subconjunto) / len(df)
        entropia_atributo += peso * calcular_entropia(subconjunto[alvo])

    ganho = entropia_total - entropia_atributo
    return ganho

def id3(df, atributos, alvo):
    classes = df[alvo].unique()
    if len(classes) == 1:
        return classes[0]
    if len(atributos) == 0:
        return df[alvo].mode()[0]

    ganhos = {atrib: ganho_informacao(df, atrib, alvo) for atrib in atributos}
    melhor_atributo = max(ganhos, key=ganhos.get)

    arvore = {melhor_atributo: {}}
    valores_unicos = df[melhor_atributo].unique()

    for valor in valores_unicos:
        subconjunto = df[df[melhor_atributo] == valor]
        if subconjunto.empty:
            arvore[melhor_atributo][valor] = df[alvo].mode()[0]
        else:
            novos_atributos = [a for a in atributos if a != melhor_atributo]
            arvore[melhor_atributo][valor] = id3(subconjunto, novos_atributos, alvo)

    return arvore

def classificar_exemplo(exemplo, arvore):
    if not isinstance(arvore, dict):
        return arvore
    atributo = next(iter(arvore))
    valor = exemplo.get(atributo)
    if valor not in arvore[atributo]:
        return "Classe desconhecida"
    ramo = arvore[atributo][valor]
    return classificar_exemplo(exemplo, ramo)

def codificar_tabuleiro(board):
    return ''.join(str(cell) for row in board for cell in row)

def prever_jogada_com_arvore(board, arvore):
    estado = codificar_tabuleiro(board)
    exemplo = {}
    for i, valor in enumerate(estado):
        exemplo[f"pos_{i}"] = valor

    jogada_prevista = classificar_exemplo(exemplo, arvore)

    try:
        col = int(jogada_prevista)
        if 0 <= col < 7 and is_empty(board, col):
            return col
        else:
            valid = [i for i in range(7) if is_empty(board, i)]
            return random.choice(valid) if valid else None
    except:
        valid = [i for i in range(7) if is_empty(board, i)]
        return random.choice(valid) if valid else None