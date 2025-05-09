import pygame
import random
import sys
import os # Importato per gestire percorsi di file in modo più robusto (opzionale ma buona pratica)

# Inizializzazione di Pygame
pygame.init()
pygame.mixer.init()

# --- Costanti e Configurazioni ---
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
YELLOW = (255, 255, 0) # Colore per l'high score

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

FPS = 10
HIGHSCORE_FILE = "highscore.txt" # Nome del file per il punteggio più alto

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('PySnake by ManiDiAmarena')
clock = pygame.time.Clock()

font_style = pygame.font.SysFont("bahnschrift", 15)
score_font = pygame.font.SysFont("comicsansms", 25) # Usato anche per high score

# Caricamento Suoni
try:
    eat_sound = pygame.mixer.Sound("eat.mp3") # o .wav/.ogg
    game_over_sound = pygame.mixer.Sound("gameover.mp3") # o .wav/.ogg
except pygame.error as e:
    print(f"Errore nel caricamento dei file audio: {e}")
    eat_sound = None
    game_over_sound = None

# --- >>> NUOVA FUNZIONE: Caricare High Score <<< ---
def load_high_score():
    """Carica il punteggio più alto dal file."""
    try:
        with open(HIGHSCORE_FILE, 'r') as f:
            score = int(f.read())
            return score
    except (IOError, ValueError): # File non trovato, vuoto o con contenuto non valido
        return 0

# --- >>> NUOVA FUNZIONE: Salvare High Score <<< ---
def save_high_score(score):
    """Salva il punteggio più alto nel file."""
    try:
        with open(HIGHSCORE_FILE, 'w') as f:
            f.write(str(score))
    except IOError:
        print(f"Errore: Impossibile salvare il punteggio più alto su {HIGHSCORE_FILE}")

# Variabile globale per il punteggio più alto, caricata una volta all'inizio
current_high_score = load_high_score()

def display_score_and_highscore(score, high_score):
    """Visualizza il punteggio corrente e il punteggio più alto."""
    score_text = score_font.render("Punteggio: " + str(score), True, BLUE)
    screen.blit(score_text, [10, 10])

    highscore_text = font_style.render("High Score: " + str(high_score), True, YELLOW) # Usiamo font_style per distinguerlo
    screen.blit(highscore_text, [10, 45]) # Posizionato sotto il punteggio corrente

def draw_snake(snake_list):
    for x, y in snake_list:
        pygame.draw.rect(screen, GREEN, [x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE])
        pygame.draw.rect(screen, BLACK, [x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE], 1)

def draw_food(food_pos):
    pygame.draw.rect(screen, RED, [food_pos[0] * GRID_SIZE, food_pos[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE])
    pygame.draw.rect(screen, BLACK, [food_pos[0] * GRID_SIZE, food_pos[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE], 1)

def display_message(msg, color, y_displacement=0, chosen_font=font_style):
    mesg = chosen_font.render(msg, True, color)
    text_rect = mesg.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + y_displacement))
    screen.blit(mesg, text_rect)

def get_random_food_position(snake_list):
    while True:
        food_x = random.randrange(0, GRID_WIDTH)
        food_y = random.randrange(0, GRID_HEIGHT)
        if (food_x, food_y) not in snake_list:
            return (food_x, food_y)

def game_loop():
    global current_high_score # Per modificare la variabile globale

    game_over = False
    game_close = False

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
            # --- >>> MODIFICA: Aggiornamento e Salvataggio High Score <<< ---
            if score > current_high_score:
                current_high_score = score
                save_high_score(current_high_score)
            # --- FINE MODIFICA ---

            screen.fill(BLACK)
            display_message("Hai perso!", RED, -60, score_font) # Spostato un po' più su
            display_message(f"Punteggio finale: {score}", BLUE, -20, font_style)
            display_message(f"High Score: {current_high_score}", YELLOW, 20, font_style) # Mostra High Score
            display_message("Premi 'R' per rigiocare o 'Q' per uscire", WHITE, 70, font_style) # Spostato un po' più giù
            pygame.display.update()

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

        if snake_head_pos[0] >= GRID_WIDTH or snake_head_pos[0] < 0 \
           or snake_head_pos[1] >= GRID_HEIGHT or snake_head_pos[1] < 0:
            game_close = True

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

        screen.fill(BLACK)
        draw_snake(snake_list)
        draw_food(food_pos)
        # --- >>> MODIFICA: Chiamata alla nuova funzione per visualizzare i punteggi <<< ---
        display_score_and_highscore(score, current_high_score)
        # --- FINE MODIFICA ---
        pygame.display.update()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    game_loop()