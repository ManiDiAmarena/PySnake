import pygame
import random
import sys
import os
import json

# Inizializzazione di tutti i moduli Pygame importati (fondamentale!)
pygame.init()
# Inizializzazione specifica per il mixer audio
pygame.mixer.init()

# --- Costanti e Configurazioni ---
SCREEN_WIDTH = 800
PANEL_HEIGHT = 60
GAME_AREA_HEIGHT = 600
SCREEN_HEIGHT = PANEL_HEIGHT + GAME_AREA_HEIGHT # Altezza totale della finestra

GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = GAME_AREA_HEIGHT // GRID_SIZE # Basato sull'area di gioco effettiva

# Colori
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 150)
YELLOW = (200, 200, 0)
PANEL_COLOR = (50, 50, 50)
MENU_TEXT_COLOR = (200, 200, 200)
MENU_HIGHLIGHT_COLOR = WHITE # Non usata attivamente in draw_button, ma definita
MENU_BUTTON_COLOR = (70, 70, 70)
MENU_BUTTON_HOVER_COLOR = (100, 100, 100)

# Direzioni
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

FPS = 10 # Frame Per Second per il gioco e il menu
LEADERBOARD_FILE = "leaderboard.json"
MAX_LEADERBOARD_ENTRIES = 10

# --- >>> DEFINIZIONE GLOBALE DI SCREEN E CLOCK <<< ---
# Queste variabili DEVONO essere definite qui, nel contesto globale,
# dopo pygame.init() e prima di essere usate da qualsiasi funzione.
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('PySnake by ManiDiAmarena')
clock = pygame.time.Clock()
# --- FINE DEFINIZIONE GLOBALE ---

# --- Font (Tornati alla selezione precedente come richiesto) ---
try:
    font_style_panel = pygame.font.SysFont("verdana", 20)
    score_font_panel = pygame.font.SysFont("arialblack", 24)
    game_over_font_big = pygame.font.SysFont("impact", 50)
    game_over_font_small = pygame.font.SysFont("verdana", 22)
    menu_font_title = pygame.font.SysFont("impact", 60)
    menu_font_options = pygame.font.SysFont("verdana", 30)
except pygame.error as e:
    print(f"Attenzione: Errore nel caricamento dei font specificati ({e}). Uso font di default.")
    font_style_panel = pygame.font.SysFont(None, 25)
    score_font_panel = pygame.font.SysFont(None, 30)
    game_over_font_big = pygame.font.SysFont(None, 55)
    game_over_font_small = pygame.font.SysFont(None, 28)
    menu_font_title = pygame.font.SysFont(None, 65)
    menu_font_options = pygame.font.SysFont(None, 35)

# --- Suoni ---
current_volume = 0.5 # Volume di default (0.0 to 1.0)
eat_sound = None
game_over_sound = None

def load_sounds():
    global eat_sound, game_over_sound, current_volume
    try:
        eat_sound = pygame.mixer.Sound("eat.mp3") # o .wav/.ogg
        game_over_sound = pygame.mixer.Sound("gameover.mp3") # o .wav/.ogg
        if eat_sound: eat_sound.set_volume(current_volume)
        if game_over_sound: game_over_sound.set_volume(current_volume)
    except pygame.error as e:
        print(f"Errore nel caricamento dei file audio: {e}")
        eat_sound = None
        game_over_sound = None

# --- Funzioni per Leaderboard ---
def load_leaderboard():
    if not os.path.exists(LEADERBOARD_FILE):
        return []
    try:
        with open(LEADERBOARD_FILE, 'r') as f:
            data = json.load(f)
            leaderboard = sorted([int(score) for score in data if isinstance(score, (int, float, str)) and str(score).isdigit()], reverse=True)
            return leaderboard[:MAX_LEADERBOARD_ENTRIES]
    except (IOError, ValueError, json.JSONDecodeError):
        return []

def save_score_to_leaderboard(new_score):
    leaderboard = load_leaderboard()
    leaderboard.append(int(new_score))
    leaderboard = sorted(list(set(leaderboard)), reverse=True)
    leaderboard = leaderboard[:MAX_LEADERBOARD_ENTRIES]
    try:
        with open(LEADERBOARD_FILE, 'w') as f:
            json.dump(leaderboard, f)
    except IOError:
        print(f"Errore: Impossibile salvare la leaderboard su {LEADERBOARD_FILE}")

# Variabile per il punteggio più alto (top della leaderboard)
top_score_value = 0 # Inizializzata, verrà aggiornata dopo il caricamento

# --- Funzioni di disegno e UI (usano 'screen' e 'clock' globali) ---
def display_score_and_highscore_panel(score, high_score_display):
    pygame.draw.rect(screen, PANEL_COLOR, [0, 0, SCREEN_WIDTH, PANEL_HEIGHT])
    score_text_surface = score_font_panel.render("Punteggio: " + str(score), True, BLUE)
    screen.blit(score_text_surface, [15, PANEL_HEIGHT // 2 - score_text_surface.get_height() // 2])
    highscore_text_surface = font_style_panel.render("Top Score: " + str(high_score_display), True, YELLOW)
    screen.blit(highscore_text_surface, [SCREEN_WIDTH - highscore_text_surface.get_width() - 15, PANEL_HEIGHT // 2 - highscore_text_surface.get_height() // 2])

def draw_snake(snake_list):
    for x, y in snake_list:
        pygame.draw.rect(screen, GREEN, [x * GRID_SIZE, PANEL_HEIGHT + y * GRID_SIZE, GRID_SIZE, GRID_SIZE])
        pygame.draw.rect(screen, BLACK, [x * GRID_SIZE, PANEL_HEIGHT + y * GRID_SIZE, GRID_SIZE, GRID_SIZE], 1)

def draw_food(food_pos):
    pygame.draw.rect(screen, RED, [food_pos[0] * GRID_SIZE, PANEL_HEIGHT + food_pos[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE])
    pygame.draw.rect(screen, BLACK, [food_pos[0] * GRID_SIZE, PANEL_HEIGHT + food_pos[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE], 1)

def display_message_game_area(msg, color, y_displacement=0, chosen_font=game_over_font_small):
    mesg = chosen_font.render(msg, True, color)
    center_x = SCREEN_WIDTH / 2
    center_y = PANEL_HEIGHT + (GAME_AREA_HEIGHT / 2) + y_displacement
    text_rect = mesg.get_rect(center=(center_x, center_y))
    screen.blit(mesg, text_rect)

def get_random_food_position(snake_list):
    while True:
        food_x = random.randrange(0, GRID_WIDTH)
        food_y = random.randrange(0, GRID_HEIGHT)
        if (food_x, food_y) not in snake_list:
            return (food_x, food_y)

def draw_button(text, font, text_color, rect, button_color, hover_color):
    mouse_pos = pygame.mouse.get_pos()
    is_hovered = rect.collidepoint(mouse_pos)

    current_button_color = hover_color if is_hovered else button_color
    pygame.draw.rect(screen, current_button_color, rect, border_radius=10)

    text_surf = font.render(text, True, text_color)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)
    return is_hovered # Restituisce se il mouse è sopra per gestire il click nell'event loop

# --- Schermate specifiche (usano 'screen' e 'clock' globali) ---
def leaderboard_screen_loop():
    global game_state, leaderboard_data
    leaderboard_data = load_leaderboard()
    running = True

    back_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 100, 200, 50)

    while running:
        mouse_clicked_this_frame = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    game_state = "MENU"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Tasto sinistro
                    mouse_clicked_this_frame = True

        screen.fill(BLACK)
        title_surf = menu_font_title.render("Leaderboard", True, YELLOW)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 80))
        screen.blit(title_surf, title_rect)

        if not leaderboard_data:
            no_scores_surf = menu_font_options.render("Nessun punteggio salvato!", True, WHITE)
            no_scores_rect = no_scores_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            screen.blit(no_scores_surf, no_scores_rect)
        else:
            y_offset = 150
            for i, score_val in enumerate(leaderboard_data):
                entry_surf = menu_font_options.render(f"{i+1}. {score_val}", True, MENU_TEXT_COLOR)
                entry_rect = entry_surf.get_rect(center=(SCREEN_WIDTH // 2, y_offset + i * 45))
                screen.blit(entry_surf, entry_rect)
                if i >= MAX_LEADERBOARD_ENTRIES -1 : break

        is_back_hovered = draw_button("Indietro", menu_font_options, WHITE, back_button_rect, MENU_BUTTON_COLOR, MENU_BUTTON_HOVER_COLOR)
        if is_back_hovered and mouse_clicked_this_frame:
            running = False
            game_state = "MENU"

        pygame.display.flip()
        clock.tick(FPS)

def settings_screen_loop():
    global game_state, current_volume
    running = True
    volume_step = 0.1

    back_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 100, 200, 50)
    vol_down_rect = pygame.Rect(SCREEN_WIDTH // 2 - 125, 250, 50, 50) # Pulsante più piccolo
    vol_up_rect = pygame.Rect(SCREEN_WIDTH // 2 + 75, 250, 50, 50) # Pulsante più piccolo


    while running:
        mouse_clicked_this_frame = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    game_state = "MENU"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_clicked_this_frame = True

        screen.fill(BLACK)
        title_surf = menu_font_title.render("Impostazioni", True, YELLOW)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 80))
        screen.blit(title_surf, title_rect)

        volume_text_surf = menu_font_options.render(f"Volume: {int(current_volume * 100)}%", True, MENU_TEXT_COLOR)
        volume_text_rect = volume_text_surf.get_rect(center=(SCREEN_WIDTH // 2, 200))
        screen.blit(volume_text_surf, volume_text_rect)

        is_vol_down_hovered = draw_button("-", menu_font_options, WHITE, vol_down_rect, MENU_BUTTON_COLOR, MENU_BUTTON_HOVER_COLOR)
        if is_vol_down_hovered and mouse_clicked_this_frame:
            current_volume = round(max(0.0, current_volume - volume_step),1)
            if eat_sound: eat_sound.set_volume(current_volume)
            if game_over_sound: game_over_sound.set_volume(current_volume)
            pygame.time.delay(100) # Debounce

        is_vol_up_hovered = draw_button("+", menu_font_options, WHITE, vol_up_rect, MENU_BUTTON_COLOR, MENU_BUTTON_HOVER_COLOR)
        if is_vol_up_hovered and mouse_clicked_this_frame:
            current_volume = round(min(1.0, current_volume + volume_step),1)
            if eat_sound: eat_sound.set_volume(current_volume)
            if game_over_sound: game_over_sound.set_volume(current_volume)
            pygame.time.delay(100) # Debounce

        is_back_hovered = draw_button("Indietro", menu_font_options, WHITE, back_button_rect, MENU_BUTTON_COLOR, MENU_BUTTON_HOVER_COLOR)
        if is_back_hovered and mouse_clicked_this_frame:
            running = False
            game_state = "MENU"

        pygame.display.flip()
        clock.tick(FPS)

# --- Ciclo di Gioco Principale (usa 'screen' e 'clock' globali) ---
def game_loop():
    global top_score_value, game_state, leaderboard_data

    game_over_flag = False
    game_close_screen = False

    snake_head_pos = [GRID_WIDTH // 2, GRID_HEIGHT // 2]
    snake_list = [[snake_head_pos[0], snake_head_pos[1]]]
    snake_length = 1
    current_direction = RIGHT
    change_to_direction = current_direction
    food_pos = get_random_food_position(snake_list)
    score = 0
    first_game_over_sound_played = False

    while not game_over_flag:
        while game_close_screen:
            if not first_game_over_sound_played:
                if score > 0:
                    save_score_to_leaderboard(score)
                    leaderboard_data = load_leaderboard()
                    if leaderboard_data: top_score_value = leaderboard_data[0]
                if game_over_sound: game_over_sound.play()
                first_game_over_sound_played = True

            screen.fill(BLACK)
            current_top = leaderboard_data[0] if leaderboard_data else 0
            display_score_and_highscore_panel(score, current_top)

            display_message_game_area("Hai perso!", RED, -70, chosen_font=game_over_font_big)
            display_message_game_area(f"Punteggio: {score}", BLUE, -20, chosen_font=game_over_font_small)
            display_message_game_area("Premi 'R' per Riprovare", WHITE, 60, chosen_font=game_over_font_small)
            display_message_game_area("'M' per Menu Principale", WHITE, 100, chosen_font=game_over_font_small)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_m:
                        game_close_screen = False; game_over_flag = True; game_state = "MENU"
                    if event.key == pygame.K_r:
                        game_loop(); return # Rigioca

        # Eventi di gioco
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a and current_direction != RIGHT: change_to_direction = LEFT
                elif event.key == pygame.K_d and current_direction != LEFT: change_to_direction = RIGHT
                elif event.key == pygame.K_w and current_direction != DOWN: change_to_direction = UP
                elif event.key == pygame.K_s and current_direction != UP: change_to_direction = DOWN
                elif event.key == pygame.K_ESCAPE:
                    game_over_flag = True; game_state = "MENU"; return

        current_direction = change_to_direction
        snake_head_pos[0] += current_direction[0]
        snake_head_pos[1] += current_direction[1]

        if not (0 <= snake_head_pos[0] < GRID_WIDTH and 0 <= snake_head_pos[1] < GRID_HEIGHT):
            game_close_screen = True
        if list(snake_head_pos) in snake_list[:-1]: game_close_screen = True
        if game_close_screen: continue

        snake_list.append(list(snake_head_pos))
        if len(snake_list) > snake_length: del snake_list[0]

        if snake_head_pos[0] == food_pos[0] and snake_head_pos[1] == food_pos[1]:
            food_pos = get_random_food_position(snake_list)
            snake_length += 1; score += 10
            if eat_sound: eat_sound.play()

        screen.fill(BLACK) # Sfondo area di gioco
        current_top = leaderboard_data[0] if leaderboard_data else 0
        display_score_and_highscore_panel(score, current_top)
        draw_snake(snake_list); draw_food(food_pos)
        pygame.display.update()
        clock.tick(FPS)

# --- Gestore di stati e Menu Principale (usa 'screen' e 'clock' globali) ---
game_state = "MENU"

def main_menu_loop():
    global game_state

    button_width = 300; button_height = 60; spacing = 20; start_y = 200
    new_game_rect = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, start_y, button_width, button_height)
    leaderboard_rect = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, start_y + (button_height + spacing), button_width, button_height)
    settings_rect = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, start_y + 2 * (button_height + spacing), button_width, button_height)
    exit_rect = pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2, start_y + 3 * (button_height + spacing), button_width, button_height)

    menu_running = True
    while menu_running:
        mouse_clicked_this_frame = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: mouse_clicked_this_frame = True

        screen.fill(BLACK)
        title_surf = menu_font_title.render("Snake Game", True, GREEN)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 100))
        screen.blit(title_surf, title_rect)

        if draw_button("Nuova Partita", menu_font_options, MENU_TEXT_COLOR, new_game_rect, MENU_BUTTON_COLOR, MENU_BUTTON_HOVER_COLOR) and mouse_clicked_this_frame:
            game_state = "GAME"; menu_running = False # Esce dal loop del menu
        if draw_button("Leaderboard", menu_font_options, MENU_TEXT_COLOR, leaderboard_rect, MENU_BUTTON_COLOR, MENU_BUTTON_HOVER_COLOR) and mouse_clicked_this_frame:
            game_state = "LEADERBOARD"; menu_running = False
        if draw_button("Impostazioni", menu_font_options, MENU_TEXT_COLOR, settings_rect, MENU_BUTTON_COLOR, MENU_BUTTON_HOVER_COLOR) and mouse_clicked_this_frame:
            game_state = "SETTINGS"; menu_running = False
        if draw_button("Esci", menu_font_options, MENU_TEXT_COLOR, exit_rect, MENU_BUTTON_COLOR, MENU_BUTTON_HOVER_COLOR) and mouse_clicked_this_frame:
            pygame.quit(); sys.exit()

        pygame.display.flip()
        clock.tick(FPS)

# --- Avvio del gioco ---
if __name__ == '__main__':
    load_sounds()
    leaderboard_data = load_leaderboard()
    if leaderboard_data:
        top_score_value = leaderboard_data[0]
    else:
        top_score_value = 0

    while True:
        if game_state == "MENU":
            main_menu_loop() # Questo loop si interrompe quando cambia stato
        elif game_state == "GAME":
            game_loop() # game_loop dovrebbe resettare game_state a "MENU" quando finisce
        elif game_state == "LEADERBOARD":
            leaderboard_screen_loop() # Anche questo resetta game_state a "MENU"
        elif game_state == "SETTINGS":
            settings_screen_loop() # Anche questo resetta game_state a "MENU"
        # Se il gioco viene chiuso da sys.exit(), questo loop si interrompe.