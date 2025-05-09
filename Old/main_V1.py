import pygame
import random
import sys # Per uscire dal gioco in modo pulito

# Inizializzazione di Pygame
pygame.init()

# --- Costanti e Configurazioni ---
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
GRID_SIZE = 20 # Dimensione di ogni blocco dello snake e del cibo
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Colori (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0) # Colore dello snake
RED = (255, 0, 0)   # Colore del cibo
BLUE = (0, 0, 255)  # Colore per il punteggio/messaggi
GRAY = (128, 128, 128) # Colore per la griglia (opzionale)

# Direzioni (non cambieremo direttamente i valori, ma utile per la logica)
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Velocità del gioco (Frame Per Second - FPS)
FPS = 10

# --- Setup della Finestra di Gioco ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('PySnake by ManiDiAmarena')
clock = pygame.time.Clock()

# --- Font per il testo ---
font_style = pygame.font.SysFont("bahnschrift", 25) # Puoi scegliere altri font
score_font = pygame.font.SysFont("comicsansms", 35)

def display_score(score):
    """Visualizza il punteggio corrente."""
    value = score_font.render("Punteggio: " + str(score), True, BLUE)
    screen.blit(value, [10, 10])

def draw_snake(snake_list):
    """Disegna lo snake sullo schermo."""
    for x, y in snake_list:
        pygame.draw.rect(screen, GREEN, [x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE])
        # Aggiungi un piccolo bordo nero per distinguere i segmenti
        pygame.draw.rect(screen, BLACK, [x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE], 1)


def draw_food(food_pos):
    """Disegna il cibo sullo schermo."""
    pygame.draw.rect(screen, RED, [food_pos[0] * GRID_SIZE, food_pos[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE])
    pygame.draw.rect(screen, BLACK, [food_pos[0] * GRID_SIZE, food_pos[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE], 1)


def display_message(msg, color, y_displacement=0, chosen_font=font_style):
    """Visualizza un messaggio al centro dello schermo."""
    mesg = chosen_font.render(msg, True, color)
    text_rect = mesg.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + y_displacement))
    screen.blit(mesg, text_rect)

def get_random_food_position(snake_list):
    """Genera una posizione casuale per il cibo, assicurandosi che non sia sullo snake."""
    while True:
        food_x = random.randrange(0, GRID_WIDTH)
        food_y = random.randrange(0, GRID_HEIGHT)
        if (food_x, food_y) not in snake_list:
            return (food_x, food_y)

def game_loop():
    """Ciclo principale del gioco."""
    game_over = False
    game_close = False # Indica se il gioco è finito e si deve mostrare la schermata di game over

    # Posizione iniziale e corpo dello snake
    # Lo snake è una lista di tuple (x, y) in coordinate di griglia
    snake_head_pos = [GRID_WIDTH // 2, GRID_HEIGHT // 2]
    snake_list = [[snake_head_pos[0], snake_head_pos[1]]] # Lista di segmenti
    snake_length = 1

    # Direzione iniziale dello snake
    current_direction = RIGHT
    change_to_direction = current_direction # Buffer per il cambio di direzione

    # Posizione iniziale del cibo
    food_pos = get_random_food_position(snake_list)

    score = 0

    while not game_over:

        while game_close:
            # Schermata di Game Over
            screen.fill(BLACK)
            display_message("Hai perso!", RED, -50, score_font)
            display_message(f"Punteggio finale: {score}", BLUE, 0, font_style)
            display_message("Premi 'R' per rigiocare o 'Q' per uscire", WHITE, 50, font_style)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True
                    game_close = False # Esce dal ciclo interno e poi da quello esterno
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_r:
                        game_loop() # Riavvia il gioco chiamando di nuovo game_loop
                        return # Esce dalla chiamata corrente di game_loop dopo il riavvio

        # --- Gestione Eventi ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a and current_direction != RIGHT: # 'A' per Sinistra
                    change_to_direction = LEFT
                elif event.key == pygame.K_d and current_direction != LEFT: # 'D' per Destra
                    change_to_direction = RIGHT
                elif event.key == pygame.K_w and current_direction != DOWN: # 'W' per Su
                    change_to_direction = UP
                elif event.key == pygame.K_s and current_direction != UP: # 'S' per Giù
                    change_to_direction = DOWN
                elif event.key == pygame.K_ESCAPE: # Tasto Esc per uscire
                    game_over = True

        current_direction = change_to_direction

        # --- Aggiornamento Logica di Gioco ---

        # Movimento dello snake
        snake_head_pos[0] += current_direction[0]
        snake_head_pos[1] += current_direction[1]

        # Controllo collisione con i bordi
        if snake_head_pos[0] >= GRID_WIDTH or snake_head_pos[0] < 0 \
           or snake_head_pos[1] >= GRID_HEIGHT or snake_head_pos[1] < 0:
            game_close = True

        # Inserisce la nuova testa dello snake
        snake_list.append(list(snake_head_pos)) # Aggiunge la nuova posizione della testa

        # Se lo snake è più lungo del dovuto, rimuove la coda
        if len(snake_list) > snake_length:
            del snake_list[0]

        # Controllo collisione con se stesso
        # (escludendo la testa stessa, quindi controlla snake_list[:-1])
        for segment in snake_list[:-1]:
            if segment == snake_head_pos:
                game_close = True
                break # Esce dal for se c'è collisione
        if game_close: # Se c'è stata collisione con se stesso, non continuare
            continue


        # Controllo collisione con il cibo
        if snake_head_pos[0] == food_pos[0] and snake_head_pos[1] == food_pos[1]:
            food_pos = get_random_food_position(snake_list)
            snake_length += 1
            score += 10
            # global FPS # Se volessi aumentare la velocità ad ogni cibo mangiato
            # FPS += 0.5

        # --- Disegno ---
        screen.fill(BLACK) # Pulisce lo schermo

        # Disegna una griglia (opzionale, per debug o estetica)
        # for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        #     pygame.draw.line(screen, GRAY, (x, 0), (x, SCREEN_HEIGHT))
        # for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
        #     pygame.draw.line(screen, GRAY, (0, y), (SCREEN_WIDTH, y))

        draw_snake(snake_list)
        draw_food(food_pos)
        display_score(score)

        pygame.display.update() # Aggiorna lo schermo

        # Controlla la velocità del gioco
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

# Avvia il gioco
if __name__ == '__main__':
    game_loop()