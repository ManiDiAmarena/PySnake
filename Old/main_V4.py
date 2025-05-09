import pygame
import random
import sys
import os

pygame.init()
pygame.mixer.init()

# --- Costanti e Configurazioni ---
SCREEN_WIDTH = 600
# SCREEN_HEIGHT originale era 400. Ora definiamo un'area per il pannello punteggi.
PANEL_HEIGHT = 60  # Altezza del pannello per i punteggi
GAME_AREA_HEIGHT = 400 # Altezza dell'area di gioco effettiva
SCREEN_HEIGHT = PANEL_HEIGHT + GAME_AREA_HEIGHT # Altezza totale della finestra

GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
# GRID_HEIGHT ora si basa sulla GAME_AREA_HEIGHT
GRID_HEIGHT = GAME_AREA_HEIGHT // GRID_SIZE

# Colori
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 150) # Un blu più scuro per il punteggio
YELLOW = (200, 200, 0) # Un giallo più scuro per l'high score
PANEL_COLOR = (50, 50, 50) # Colore di sfondo per il pannello punteggi

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

FPS = 10
HIGHSCORE_FILE = "highscore.txt"

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('PySnake by ManiDiAmarena')
clock = pygame.time.Clock()

# --- >>> MODIFICA: Scelta dei Font <<< ---
# Puoi provare diversi font di sistema. Alcuni comuni sono:
# "arial", "verdana", "timesnewroman", "calibri", "consolas", "tahoma"
# Se hai un file font .ttf (es. "my_custom_font.ttf") nella stessa cartella dello script:
# font_style = pygame.font.Font("my_custom_font.ttf", 22)
# score_font = pygame.font.Font("my_custom_font.ttf", 30)
# Per ora usiamo dei font di sistema diversi:
try:
    # Font per messaggi generici e high score nel pannello
    font_style_panel = pygame.font.SysFont("verdana", 20)
    # Font per il punteggio corrente nel pannello
    score_font_panel = pygame.font.SysFont("arialblack", 24)
    # Font per messaggi di game over (più grandi)
    game_over_font_big = pygame.font.SysFont("impact", 50)
    game_over_font_small = pygame.font.SysFont("verdana", 22)

except pygame.error as e:
    print(f"Attenzione: Errore nel caricamento dei font specificati ({e}). Uso font di default.")
    font_style_panel = pygame.font.SysFont(None, 25) # Font di default
    score_font_panel = pygame.font.SysFont(None, 30) # Font di default
    game_over_font_big = pygame.font.SysFont(None, 55)
    game_over_font_small = pygame.font.SysFont(None, 28)
# --- FINE MODIFICA FONT ---

# Caricamento Suoni
try:
    eat_sound = pygame.mixer.Sound("eat.mp3")
    game_over_sound = pygame.mixer.Sound("gameover.mp3")
except pygame.error as e:
    print(f"Errore nel caricamento dei file audio: {e}")
    eat_sound = None
    game_over_sound = None

def load_high_score():
    try:
        with open(HIGHSCORE_FILE, 'r') as f:
            score = int(f.read())
            return score
    except (IOError, ValueError):
        return 0

def save_high_score(score):
    try:
        with open(HIGHSCORE_FILE, 'w') as f:
            f.write(str(score))
    except IOError:
        print(f"Errore: Impossibile salvare il punteggio più alto su {HIGHSCORE_FILE}")

current_high_score = load_high_score()

# --- >>> MODIFICA: Visualizzazione punteggi nel pannello <<< ---
def display_score_and_highscore_panel(score, high_score):
    """Visualizza i punteggi nel pannello superiore."""
    # Disegna lo sfondo del pannello
    pygame.draw.rect(screen, PANEL_COLOR, [0, 0, SCREEN_WIDTH, PANEL_HEIGHT])

    score_text_surface = score_font_panel.render("Punteggio: " + str(score), True, BLUE)
    # Posiziona il testo del punteggio all'interno del pannello
    screen.blit(score_text_surface, [15, PANEL_HEIGHT // 2 - score_text_surface.get_height() // 2])

    highscore_text_surface = font_style_panel.render("High Score: " + str(high_score), True, YELLOW)
    # Posiziona l'high score sulla destra del pannello
    screen.blit(highscore_text_surface, [SCREEN_WIDTH - highscore_text_surface.get_width() - 15, PANEL_HEIGHT // 2 - highscore_text_surface.get_height() // 2])
# --- FINE MODIFICA ---

# --- >>> MODIFICA: Disegno snake e cibo con offset per il pannello <<< ---
def draw_snake(snake_list):
    for x, y in snake_list:
        # Aggiungiamo PANEL_HEIGHT alla coordinata y per disegnare sotto il pannello
        pygame.draw.rect(screen, GREEN, [x * GRID_SIZE, PANEL_HEIGHT + y * GRID_SIZE, GRID_SIZE, GRID_SIZE])
        pygame.draw.rect(screen, BLACK, [x * GRID_SIZE, PANEL_HEIGHT + y * GRID_SIZE, GRID_SIZE, GRID_SIZE], 1)

def draw_food(food_pos):
    # Aggiungiamo PANEL_HEIGHT alla coordinata y
    pygame.draw.rect(screen, RED, [food_pos[0] * GRID_SIZE, PANEL_HEIGHT + food_pos[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE])
    pygame.draw.rect(screen, BLACK, [food_pos[0] * GRID_SIZE, PANEL_HEIGHT + food_pos[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE], 1)
# --- FINE MODIFICA ---

def display_message(msg, color, y_displacement=0, chosen_font=game_over_font_small): # Font di default per game over
    """Visualizza un messaggio al centro dell'AREA DI GIOCO."""
    mesg = chosen_font.render(msg, True, color)
    # Calcola il centro rispetto all'area di gioco (sotto il pannello)
    center_x = SCREEN_WIDTH / 2
    center_y = PANEL_HEIGHT + (GAME_AREA_HEIGHT / 2) + y_displacement
    text_rect = mesg.get_rect(center=(center_x, center_y))
    screen.blit(mesg, text_rect)

def get_random_food_position(snake_list):
    """Genera cibo nell'area di gioco definita da GRID_WIDTH e GRID_HEIGHT."""
    while True:
        food_x = random.randrange(0, GRID_WIDTH)
        # GRID_HEIGHT è già calcolata in base alla GAME_AREA_HEIGHT
        food_y = random.randrange(0, GRID_HEIGHT)
        if (food_x, food_y) not in snake_list:
            return (food_x, food_y)

def game_loop():
    global current_high_score

    game_over = False
    game_close = False

    # Lo snake inizia al centro della *nuova* area di gioco
    snake_head_pos = [GRID_WIDTH // 2, GRID_HEIGHT // 2]
    snake_list = [[snake_head_pos[0], snake_head_pos[1]]]
    snake_length = 1

    current_direction = RIGHT
    change_to_direction = current_direction

    food_pos = get_random_food_position(snake_list)
    score = 0

    first_game_over_sound_played = False

    while not game_over:
        while game_close:
            if score > current_high_score:
                current_high_score = score
                save_high_score(current_high_score)

            # Sfondo per l'intera finestra (incluso il pannello, anche se verrà ridisegnato)
            screen.fill(BLACK)
            # Ridisegna il pannello con i punteggi finali (opzionale, o integra nel messaggio sotto)
            display_score_and_highscore_panel(score, current_high_score)


            display_message("Hai perso!", RED, -70, chosen_font=game_over_font_big)
            display_message(f"Punteggio finale: {score}", BLUE, -20, chosen_font=game_over_font_small)
            display_message(f"High Score: {current_high_score}", YELLOW, 20, chosen_font=game_over_font_small)
            display_message("Premi 'R' per rigiocare o 'Q' per uscire", WHITE, 80, chosen_font=game_over_font_small)
            pygame.display.update() # Aggiorna una volta per la schermata di game over

            if game_over_sound and not first_game_over_sound_played:
                game_over_sound.play()
                first_game_over_sound_played = True

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True
                    game_close = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_r:
                        game_loop()
                        return
        # Gestione Eventi
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a and current_direction != RIGHT:
                    change_to_direction = LEFT
                elif event.key == pygame.K_d and current_direction != LEFT:
                    change_to_direction = RIGHT
                elif event.key == pygame.K_w and current_direction != DOWN:
                    change_to_direction = UP
                elif event.key == pygame.K_s and current_direction != UP:
                    change_to_direction = DOWN
                elif event.key == pygame.K_ESCAPE:
                    game_over = True

        current_direction = change_to_direction
        snake_head_pos[0] += current_direction[0]
        snake_head_pos[1] += current_direction[1]

        # --- MODIFICA: Collisione con i bordi dell'AREA DI GIOCO ---
        # GRID_HEIGHT è già corretto per l'area di gioco
        if snake_head_pos[0] >= GRID_WIDTH or snake_head_pos[0] < 0 \
           or snake_head_pos[1] >= GRID_HEIGHT or snake_head_pos[1] < 0:
            game_close = True
        # --- FINE MODIFICA ---

        snake_list.append(list(snake_head_pos))
        if len(snake_list) > snake_length:
            del snake_list[0]

        for segment in snake_list[:-1]:
            if segment == snake_head_pos:
                game_close = True
                break
        if game_close:
            continue

        if snake_head_pos[0] == food_pos[0] and snake_head_pos[1] == food_pos[1]:
            food_pos = get_random_food_position(snake_list)
            snake_length += 1
            score += 10
            if eat_sound:
                eat_sound.play()

        # Disegno
        screen.fill(BLACK) # Sfondo dell'area di gioco
        # Disegna prima il pannello dei punteggi
        display_score_and_highscore_panel(score, current_high_score)
        # Poi disegna gli elementi del gioco (snake, cibo) nell'area sottostante
        draw_snake(snake_list)
        draw_food(food_pos)

        pygame.display.update()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    game_loop()