import pygame
import sys
import time
import math
import copy
import pandas as pd
from button import Button
import os
from game_logic import (
    create_board, is_empty, check_next_empty_row, put_piece, win, 
    ROW_COUNT, COLUMN_COUNT
)
from ai_algorithms import (
    minimax, monte_carlo, monte_carlo_difficulty, a_star, a_star_with_level,
    id3, prever_jogada_com_arvore
)


pygame.init()

WIDTH = 1280
HEIGHT = 720
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Connect 4 AI")


BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)


try:
    BG = pygame.image.load("../assets/Background.png")
    PLAY_IMG = pygame.image.load("../assets/Play Rect.png")
    QUIT_IMG = pygame.image.load("../assets/Quit Rect.png")
    FONT_PATH = "../assets/font.ttf"
except FileNotFoundError:
    print("Error: Assets not found.")
    sys.exit()

def get_font(size):
    return pygame.font.Font(FONT_PATH, size)

c4_tree_full = None

# Helper methods

def draw_board(board):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(SCREEN, BLUE, (c * 180.8, r * 120, 182.8, 120))
            pygame.draw.circle(SCREEN, BLACK, (c * 182.8 + 91.4, r * 105 + 60), 50)

    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            if board[r][c] == 1:
                pygame.draw.circle(SCREEN, RED, (c * 182.8 + 91.4, 586 - r * 105), 52)
            elif board[r][c] == 2:
                pygame.draw.circle(SCREEN, YELLOW, (c * 182.8 + 91.4, 586 - r * 105), 52)
    
    # Botão de voltar desenhado aqui para persistir durante o jogo, 
    # mas a lógica de clique é gerida no loop do jogo.
    BACK_TEXT = get_font(40).render("BACK", True, "Black")
    SCREEN.blit(BACK_TEXT, (1100, 675))
    
    pygame.display.update()

# Loops

def pvp_game():
    board = create_board()
    game_over = False
    turn = 0
    draw_board(board)

    BACK_BUTTON = Button(image=None, pos=(1150, 690), text_input="BACK", font=get_font(40), base_color="Black", hovering_color="Green")

    while not game_over:
        MOUSE_POS = pygame.mouse.get_pos()
        BACK_BUTTON.changeColor(MOUSE_POS)
        BACK_BUTTON.update(SCREEN)
        pygame.display.update() 

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if BACK_BUTTON.checkForInput(MOUSE_POS):
                    return 

                posx = event.pos[0]
                if posx < 1100:
                    col = int(posx // 182.8)
                    player = 1 if turn == 0 else 2

                    if is_empty(board, col):
                        row = check_next_empty_row(board, col)
                        put_piece(board, row, col, player)

                        if win(player, board):
                            print(f'Player {player} wins!')
                            game_over = True
                            draw_board(board)
                            time.sleep(3)
                            return

                        turn = (turn + 1) % 2
                        draw_board(board)
    return

def a_star_game():
    board = create_board()
    game_over = False
    turn = 0
    draw_board(board)
    BACK_BUTTON = Button(image=None, pos=(1150, 690), text_input="BACK", font=get_font(40), base_color="Black", hovering_color="Green")

    while not game_over:
        MOUSE_POS = pygame.mouse.get_pos()
        BACK_BUTTON.update(SCREEN)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if BACK_BUTTON.checkForInput(MOUSE_POS): return
                
                if turn == 0:
                    posx = event.pos[0]
                    col = int(posx // 182.8)
                    if is_empty(board, col):
                        row = check_next_empty_row(board, col)
                        put_piece(board, row, col, 1)
                        if win(1, board):
                            print('Player 1 wins!')
                            game_over = True
                        turn = 1
                        draw_board(board)

        if turn == 1 and not game_over:
            time.sleep(1)
            col = a_star(board)
            if col is not None and is_empty(board, col):
                row = check_next_empty_row(board, col)
                put_piece(board, row, col, 2)
                if win(2, board):
                    print('AI wins!')
                    game_over = True
                turn = 0
                draw_board(board)
            else:
                print("Draw or error on IA")
                game_over = True

    time.sleep(3)

def a_star_game_with_difficulty(level):
    board = create_board()
    game_over = False
    turn = 0
    draw_board(board)
    BACK_BUTTON = Button(image=None, pos=(1150, 690), text_input="BACK", font=get_font(40), base_color="Black", hovering_color="Green")

    while not game_over:
        MOUSE_POS = pygame.mouse.get_pos()
        BACK_BUTTON.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if BACK_BUTTON.checkForInput(MOUSE_POS): return
                if turn == 0:
                    col = int(event.pos[0] // 182.8)
                    if is_empty(board, col):
                        row = check_next_empty_row(board, col)
                        put_piece(board, row, col, 1)
                        if win(1, board):
                            print("Player 1 wins!")
                            game_over = True
                        turn = 1
                        draw_board(board)

        if turn == 1 and not game_over:
            time.sleep(0.5)
            col = a_star_with_level(board, level)
            if col is not None and is_empty(board, col):
                row = check_next_empty_row(board, col)
                put_piece(board, row, col, 2)
                if win(2, board):
                    print("AI wins!")
                    game_over = True
                turn = 0
                draw_board(board)

    time.sleep(3)

def mc_game():
    board = create_board()
    game_over = False
    turn = 0
    draw_board(board)
    BACK_BUTTON = Button(image=None, pos=(1150, 690), text_input="BACK", font=get_font(40), base_color="Black", hovering_color="Green")

    while not game_over:
        MOUSE_POS = pygame.mouse.get_pos()
        BACK_BUTTON.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if BACK_BUTTON.checkForInput(MOUSE_POS): return
                if turn == 0:
                    col = int(event.pos[0] // 182.8)
                    if is_empty(board, col):
                        row = check_next_empty_row(board, col)
                        put_piece(board, row, col, 1)
                        if win(1, board): game_over = True
                        turn = 1
                        draw_board(board)

        if turn == 1 and not game_over:
            col = monte_carlo(board)
            if col is not None and is_empty(board, col):
                row = check_next_empty_row(board, col)
                put_piece(board, row, col, 2)
                if win(2, board): game_over = True
                turn = 0
                draw_board(board)
    
    time.sleep(3)

def monte_carlo_game_custom(simulations):
    board = create_board()
    game_over = False
    turn = 0
    draw_board(board)
    BACK_BUTTON = Button(image=None, pos=(1150, 690), text_input="BACK", font=get_font(40), base_color="Black", hovering_color="Green")

    while not game_over:
        MOUSE_POS = pygame.mouse.get_pos()
        BACK_BUTTON.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if BACK_BUTTON.checkForInput(MOUSE_POS): return
                if turn == 0:
                    col = int(event.pos[0] // 182.8)
                    if is_empty(board, col):
                        row = check_next_empty_row(board, col)
                        put_piece(board, row, col, 1)
                        if win(1, board): game_over = True
                        turn = 1
                        draw_board(board)

        if turn == 1 and not game_over:
            time.sleep(0.5)
            col = monte_carlo_difficulty(board, player_num=2, simulations=simulations)
            if col is not None and is_empty(board, col):
                row = check_next_empty_row(board, col)
                put_piece(board, row, col, 2)
                if win(2, board): game_over = True
                turn = 0
                draw_board(board)
    time.sleep(3)

def minimax_game_with_difficulty(depth):
    board = create_board()
    game_over = False
    turn = 0
    draw_board(board)
    BACK_BUTTON = Button(image=None, pos=(1150, 690), text_input="BACK", font=get_font(40), base_color="Black", hovering_color="Green")

    while not game_over:
        MOUSE_POS = pygame.mouse.get_pos()
        BACK_BUTTON.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if BACK_BUTTON.checkForInput(MOUSE_POS): return
                if turn == 0:
                    col = int(event.pos[0] // 182.8)
                    if is_empty(board, col):
                        row = check_next_empty_row(board, col)
                        put_piece(board, row, col, 1)
                        if win(1, board): game_over = True
                        turn = 1
                        draw_board(board)

        if turn == 1 and not game_over:
            time.sleep(0.5)
            col, score = minimax(board, depth, -math.inf, math.inf, True)
            if col is not None and is_empty(board, col):
                row = check_next_empty_row(board, col)
                put_piece(board, row, col, 2)
                if win(2, board): game_over = True
                turn = 0
                draw_board(board)
    time.sleep(3)

def ia_vs_ia_game(ia1, ia2):
    board = create_board()
    game_over = False
    turn = 0
    draw_board(board)
    BACK_BUTTON = Button(image=None, pos=(1150, 690), text_input="BACK", font=get_font(40), base_color="Black", hovering_color="Green")

    while not game_over:
        MOUSE_POS = pygame.mouse.get_pos()
        BACK_BUTTON.update(SCREEN)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if BACK_BUTTON.checkForInput(MOUSE_POS): return

        # Logic
        current_ia = ia1 if turn == 0 else ia2
        player_id = 1 if turn == 0 else 2
        
        time.sleep(0.5)
        col = None
        
        if current_ia == "Monte Carlo":
            col = monte_carlo(board, player_num=player_id, time_limit=1)
        elif current_ia == "Minimax":
            col, _ = minimax(board, 4, -math.inf, math.inf, True if player_id == 2 else False) 
        elif current_ia == "A*":
            col = a_star_with_level(board, 4)

        if col is not None and is_empty(board, col):
            row = check_next_empty_row(board, col)
            put_piece(board, row, col, player_id)
            if win(player_id, board):
                print(f"IA {player_id} ({current_ia}) venceu!")
                game_over = True
            turn = 1 - turn
            draw_board(board)
        else:
            print("Erro ou Empate")
            game_over = True
            
    time.sleep(5)

def pr_game():
    global c4_tree_full
    if c4_tree_full is None:
        print("Tree not trained. Starting training...")
        try:
            df = pd.read_csv("../data/dataset_connect4.csv")
            for i in range(42):
                df[f"pos_{i}"] = df["estado"].str[i]
            df = df.drop(columns=["estado"])
            
            attributes = [f"pos_{i}" for i in range(42)]
            c4_tree_full = id3(df, attributes, "jogada")
            print("Treino concluído.")
        except Exception as e:
            print(f"Erro ao carregar dataset: {e}")
            return

    board = create_board()
    game_over = False
    turn = 0
    draw_board(board)
    BACK_BUTTON = Button(image=None, pos=(1150, 690), text_input="BACK", font=get_font(40), base_color="Black", hovering_color="Green")

    while not game_over:
        MOUSE_POS = pygame.mouse.get_pos()
        BACK_BUTTON.update(SCREEN)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if BACK_BUTTON.checkForInput(MOUSE_POS): return
                if turn == 0:
                    col = int(event.pos[0] // 182.8)
                    if is_empty(board, col):
                        row = check_next_empty_row(board, col)
                        put_piece(board, row, col, 1)
                        if win(1, board): game_over = True
                        turn = 1
                        draw_board(board)

        if turn == 1 and not game_over:
            time.sleep(1)
            col = prever_jogada_com_arvore(board, c4_tree_full)
            if col is not None and is_empty(board, col):
                row = check_next_empty_row(board, col)
                put_piece(board, row, col, 2)
                if win(2, board): game_over = True
                turn = 0
                draw_board(board)
    time.sleep(3)



def a_star_difficulty_menu():
    while True:
        SCREEN.blit(BG, (0, 0))
        MOUSE_POS = pygame.mouse.get_pos()
        MENU_TEXT = get_font(80).render("A* - Difficulty", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(640, 100))
        SCREEN.blit(MENU_TEXT, MENU_RECT)

        EASY_BUTTON = Button(image=PLAY_IMG, pos=(370, 250), text_input="EASY", font=get_font(45), base_color="#d7fcd4", hovering_color="White")
        MEDIUM_BUTTON = Button(image=PLAY_IMG, pos=(370, 350), text_input="MEDIUM", font=get_font(45), base_color="#d7fcd4", hovering_color="White")
        HARD_BUTTON = Button(image=PLAY_IMG, pos=(370, 450), text_input="HARD", font=get_font(45), base_color="#d7fcd4", hovering_color="White")
        BACK_BUTTON = Button(image=QUIT_IMG, pos=(910, 600), text_input="BACK", font=get_font(45), base_color="#d7fcd4", hovering_color="White")

        for button in [EASY_BUTTON, MEDIUM_BUTTON, HARD_BUTTON, BACK_BUTTON]:
            button.changeColor(MOUSE_POS)
            button.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if EASY_BUTTON.checkForInput(MOUSE_POS): a_star_game_with_difficulty(1)
                if MEDIUM_BUTTON.checkForInput(MOUSE_POS): a_star_game_with_difficulty(2)
                if HARD_BUTTON.checkForInput(MOUSE_POS): a_star_game_with_difficulty(3)
                if BACK_BUTTON.checkForInput(MOUSE_POS): return

        pygame.display.update()

def minimax_difficulty_menu():
    while True:
        SCREEN.blit(BG, (0, 0))
        MOUSE_POS = pygame.mouse.get_pos()
        MENU_TEXT = get_font(80).render("MINIMAX - Difficulty", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(640, 100))
        SCREEN.blit(MENU_TEXT, MENU_RECT)

        EASY_BUTTON = Button(image=PLAY_IMG, pos=(370, 250), text_input="EASY", font=get_font(45), base_color="#d7fcd4", hovering_color="White")
        MEDIUM_BUTTON = Button(image=PLAY_IMG, pos=(370, 350), text_input="MEDIUM", font=get_font(45), base_color="#d7fcd4", hovering_color="White")
        HARD_BUTTON = Button(image=PLAY_IMG, pos=(370, 450), text_input="HARD", font=get_font(45), base_color="#d7fcd4", hovering_color="White")
        BACK_BUTTON = Button(image=QUIT_IMG, pos=(910, 600), text_input="BACK", font=get_font(45), base_color="#d7fcd4", hovering_color="White")

        for button in [EASY_BUTTON, MEDIUM_BUTTON, HARD_BUTTON, BACK_BUTTON]:
            button.changeColor(MOUSE_POS)
            button.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if EASY_BUTTON.checkForInput(MOUSE_POS): minimax_game_with_difficulty(2)
                if MEDIUM_BUTTON.checkForInput(MOUSE_POS): minimax_game_with_difficulty(4)
                if HARD_BUTTON.checkForInput(MOUSE_POS): minimax_game_with_difficulty(6)
                if BACK_BUTTON.checkForInput(MOUSE_POS): return

        pygame.display.update()

def monte_carlo_difficulty_menu():
    while True:
        SCREEN.blit(BG, (0, 0))
        MOUSE_POS = pygame.mouse.get_pos()
        MENU_TEXT = get_font(80).render("MC - Difficulty", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(640, 100))
        SCREEN.blit(MENU_TEXT, MENU_RECT)

        EASY_BUTTON = Button(image=PLAY_IMG, pos=(370, 250), text_input="EASY", font=get_font(45), base_color="#d7fcd4", hovering_color="White")
        MEDIUM_BUTTON = Button(image=PLAY_IMG, pos=(370, 350), text_input="MEDIUM", font=get_font(45), base_color="#d7fcd4", hovering_color="White")
        HARD_BUTTON = Button(image=PLAY_IMG, pos=(370, 450), text_input="HARD", font=get_font(45), base_color="#d7fcd4", hovering_color="White")
        BACK_BUTTON = Button(image=QUIT_IMG, pos=(910, 600), text_input="BACK", font=get_font(45), base_color="#d7fcd4", hovering_color="White")

        for button in [EASY_BUTTON, MEDIUM_BUTTON, HARD_BUTTON, BACK_BUTTON]:
            button.changeColor(MOUSE_POS)
            button.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if EASY_BUTTON.checkForInput(MOUSE_POS): monte_carlo_game_custom(30)
                if MEDIUM_BUTTON.checkForInput(MOUSE_POS): monte_carlo_game_custom(100)
                if HARD_BUTTON.checkForInput(MOUSE_POS): monte_carlo_game_custom(500)
                if BACK_BUTTON.checkForInput(MOUSE_POS): return

        pygame.display.update()

def ia_vs_ia_menu():
    ia_options = ["Monte Carlo", "Minimax", "A*"]
    ia1_index = 0
    ia2_index = 1

    while True:
        SCREEN.blit(BG, (0, 0))
        MOUSE_POS = pygame.mouse.get_pos()

        TITLE = get_font(70).render("IA VS IA", True, "#b68f40")
        TITLE_RECT = TITLE.get_rect(center=(640, 100))
        SCREEN.blit(TITLE, TITLE_RECT)

        IA1_TEXT = get_font(40).render("IA 1: " + ia_options[ia1_index], True, "White")
        IA1_RECT = IA1_TEXT.get_rect(center=(400, 250))
        SCREEN.blit(IA1_TEXT, IA1_RECT)

        IA2_TEXT = get_font(40).render("IA 2: " + ia_options[ia2_index], True, "White")
        IA2_RECT = IA2_TEXT.get_rect(center=(880, 250))
        SCREEN.blit(IA2_TEXT, IA2_RECT)

        LEFT1 = Button(image=None, pos=(300, 250), text_input="<", font=get_font(40), base_color="White", hovering_color="Green")
        RIGHT1 = Button(image=None, pos=(500, 250), text_input=">", font=get_font(40), base_color="White", hovering_color="Green")
        LEFT2 = Button(image=None, pos=(780, 250), text_input="<", font=get_font(40), base_color="White", hovering_color="Green")
        RIGHT2 = Button(image=None, pos=(980, 250), text_input=">", font=get_font(40), base_color="White", hovering_color="Green")

        PLAY_BUTTON = Button(image=None, pos=(640, 400), text_input="PLAY", font=get_font(50), base_color="White", hovering_color="Green")
        BACK_BUTTON = Button(image=None, pos=(640, 500), text_input="BACK", font=get_font(40), base_color="White", hovering_color="Green")

        for button in [LEFT1, RIGHT1, LEFT2, RIGHT2, PLAY_BUTTON, BACK_BUTTON]:
            button.changeColor(MOUSE_POS)
            button.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if LEFT1.checkForInput(MOUSE_POS): ia1_index = (ia1_index - 1) % len(ia_options)
                if RIGHT1.checkForInput(MOUSE_POS): ia1_index = (ia1_index + 1) % len(ia_options)
                if LEFT2.checkForInput(MOUSE_POS): ia2_index = (ia2_index - 1) % len(ia_options)
                if RIGHT2.checkForInput(MOUSE_POS): ia2_index = (ia2_index + 1) % len(ia_options)
                if PLAY_BUTTON.checkForInput(MOUSE_POS): ia_vs_ia_game(ia_options[ia1_index], ia_options[ia2_index])
                if BACK_BUTTON.checkForInput(MOUSE_POS): return

        pygame.display.update()

def main_menu():
    while True:
        SCREEN.blit(BG, (0, 0))
        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = get_font(100).render("MAIN MENU", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(640, 100))

        ASTAR_BUTTON = Button(image=PLAY_IMG, pos=(370, 250), text_input="A*", font=get_font(75), base_color="#b68f40", hovering_color="White")
        MC_BUTTON = Button(image=PLAY_IMG, pos=(370, 380), text_input="MONTE CARLO", font=get_font(30), base_color="#b68f40", hovering_color="White")
        PVP_BUTTON = Button(image=PLAY_IMG, pos=(370, 510), text_input="PVP", font=get_font(75), base_color="#b68f40", hovering_color="White")
        MINIMAX_BUTTON = Button(image=PLAY_IMG, pos=(910, 250), text_input="MINIMAX", font=get_font(45), base_color="#b68f40", hovering_color="White")
        IA_BUTTON = Button(image=PLAY_IMG, pos=(910, 380), text_input="IA", font=get_font(75), base_color="#b68f40", hovering_color="White")
        PR_BUTTON = Button(image=PLAY_IMG, pos=(910, 510), text_input="PR", font=get_font(45), base_color="#b68f40", hovering_color="White")
        QUIT_BUTTON = Button(image=QUIT_IMG, pos=(640, 650), text_input="BACK", font=get_font(45), base_color="#b68f40", hovering_color="White")

        SCREEN.blit(MENU_TEXT, MENU_RECT)

        for button in [ASTAR_BUTTON, MC_BUTTON, PVP_BUTTON, MINIMAX_BUTTON, IA_BUTTON, PR_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if ASTAR_BUTTON.checkForInput(MENU_MOUSE_POS): a_star_difficulty_menu()
                if MC_BUTTON.checkForInput(MENU_MOUSE_POS): monte_carlo_difficulty_menu()
                if PVP_BUTTON.checkForInput(MENU_MOUSE_POS): pvp_game()
                if MINIMAX_BUTTON.checkForInput(MENU_MOUSE_POS): minimax_difficulty_menu()
                if PR_BUTTON.checkForInput(MENU_MOUSE_POS): pr_game()
                if IA_BUTTON.checkForInput(MENU_MOUSE_POS): ia_vs_ia_menu()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS): pygame.quit(); sys.exit()

        pygame.display.update()

if __name__ == "__main__":
    main_menu()