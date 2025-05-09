import pygame
import random
import sys
import os
import json

pygame.init()
pygame.mixer.init()

# --- Costanti e Configurazioni ---
SCREEN_WIDTH = 800
PANEL_HEIGHT = 60
GAME_AREA_HEIGHT = 600
SCREEN_HEIGHT = PANEL_HEIGHT + GAME_AREA_HEIGHT

GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = GAME_AREA_HEIGHT // GRID_SIZE

BLACK = (0,0,0); WHITE = (255,255,255); GREEN = (0,255,0); RED = (255,0,0)
BLUE = (0,0,150); YELLOW = (200,200,0); PANEL_COLOR = (50,50,50)
MENU_TEXT_COLOR = (200,200,200); MENU_BUTTON_COLOR = (70,70,70)
MENU_BUTTON_HOVER_COLOR = (100,100,100); INPUT_BOX_COLOR_ACTIVE = (200,200,200)
TEXT_INPUT_COLOR = BLACK
PAUSE_OVERLAY_COLOR = (0,0,0,180) # Nero semi-trasparente per l'overlay di pausa

UP=(0,-1); DOWN=(0,1); LEFT=(-1,0); RIGHT=(1,0)

INITIAL_FPS=8; MAX_FPS=50; FPS_INCREMENT_PER_FOOD=0.5; UI_FPS=15

LEADERBOARD_FILE="leaderboard.json"; MAX_LEADERBOARD_ENTRIES=10; MAX_NAME_LENGTH=10

try:
    screen=pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
    pygame.display.set_caption('PySnake by ManiDiAmarena')
    clock=pygame.time.Clock()
except Exception as e: print(f"CRITICAL ERROR initializing screen or clock: {e}"); pygame.quit(); sys.exit()

try:
    font_style_panel=pygame.font.SysFont("verdana",20); score_font_panel=pygame.font.SysFont("arialblack",24)
    game_over_font_big=pygame.font.SysFont("impact",50); game_over_font_small=pygame.font.SysFont("verdana",22)
    menu_font_title=pygame.font.SysFont("impact",60); menu_font_options=pygame.font.SysFont("verdana",30)
    input_font=pygame.font.SysFont("verdana",28)
    pause_menu_font = pygame.font.SysFont("verdana", 35) # Font per il menu di pausa
except pygame.error as e:
    print(f"Attenzione: Errore caricamento font ({e}). Uso default."); font_style_panel=pygame.font.SysFont(None,25)
    score_font_panel=pygame.font.SysFont(None,30); game_over_font_big=pygame.font.SysFont(None,55)
    game_over_font_small=pygame.font.SysFont(None,28); menu_font_title=pygame.font.SysFont(None,65)
    menu_font_options=pygame.font.SysFont(None,35); input_font=pygame.font.SysFont(None,32)
    pause_menu_font = pygame.font.SysFont(None, 40)

current_volume=0.5; eat_sound=None; game_over_sound=None
def load_sounds():
    global eat_sound,game_over_sound,current_volume
    try:
        eat_sound=pygame.mixer.Sound("eat.mp3"); game_over_sound=pygame.mixer.Sound("game_over.mp3")
        if eat_sound: eat_sound.set_volume(current_volume)
        if game_over_sound: game_over_sound.set_volume(current_volume)
    except pygame.error as e: print(f"Errore caricamento audio: {e}"); eat_sound=None; game_over_sound=None

def load_leaderboard():
    if not os.path.exists(LEADERBOARD_FILE): return []
    try:
        with open(LEADERBOARD_FILE,'r') as f: data=json.load(f)
        if not isinstance(data,list): return []
        valid_entries=[]
        for entry in data:
            if isinstance(entry,dict) and "name" in entry and "score" in entry and \
               isinstance(entry["name"],str) and isinstance(entry["score"],int): valid_entries.append(entry)
        return sorted(valid_entries,key=lambda x:x["score"],reverse=True)[:MAX_LEADERBOARD_ENTRIES]
    except(IOError,ValueError,json.JSONDecodeError): return []

def add_entry_to_leaderboard(name,score_val):
    leaderboard=load_leaderboard(); leaderboard.append({"name":name,"score":int(score_val)})
    leaderboard=sorted(leaderboard,key=lambda x:x["score"],reverse=True)[:MAX_LEADERBOARD_ENTRIES]
    try:
        with open(LEADERBOARD_FILE,'w') as f: json.dump(leaderboard,f,indent=2)
    except IOError: print(f"Errore salvataggio leaderboard: {LEADERBOARD_FILE}")

def check_if_qualifies(score_val,leaderboard):
    if len(leaderboard)<MAX_LEADERBOARD_ENTRIES: return True
    if not leaderboard: return True
    return score_val > leaderboard[-1]["score"]

top_score_value=0; leaderboard_data=[]; current_score_for_name_entry=0; game_state="MENU"

def display_score_and_highscore_panel(score,high_score_display_val): # Invariata
    pygame.draw.rect(screen,PANEL_COLOR,[0,0,SCREEN_WIDTH,PANEL_HEIGHT])
    score_text_surface=score_font_panel.render("Punteggio: "+str(score),True,BLUE)
    screen.blit(score_text_surface,[15,PANEL_HEIGHT//2-score_text_surface.get_height()//2])
    highscore_text_surface=font_style_panel.render("Top Score: "+str(high_score_display_val),True,YELLOW)
    screen.blit(highscore_text_surface,[SCREEN_WIDTH-highscore_text_surface.get_width()-15,PANEL_HEIGHT//2-highscore_text_surface.get_height()//2])

def draw_snake(snake_list): # Invariata
    for x,y in snake_list:
        pygame.draw.rect(screen,GREEN,[x*GRID_SIZE,PANEL_HEIGHT+y*GRID_SIZE,GRID_SIZE,GRID_SIZE])
        pygame.draw.rect(screen,BLACK,[x*GRID_SIZE,PANEL_HEIGHT+y*GRID_SIZE,GRID_SIZE,GRID_SIZE],1)

def draw_food(food_pos): # Invariata
    pygame.draw.rect(screen,RED,[food_pos[0]*GRID_SIZE,PANEL_HEIGHT+food_pos[1]*GRID_SIZE,GRID_SIZE,GRID_SIZE])
    pygame.draw.rect(screen,BLACK,[food_pos[0]*GRID_SIZE,PANEL_HEIGHT+food_pos[1]*GRID_SIZE,GRID_SIZE,GRID_SIZE],1)

def display_message_game_area(msg,color,y_displacement=0,chosen_font=game_over_font_small): # Invariata
    mesg=chosen_font.render(msg,True,color)
    text_rect=mesg.get_rect(center=(SCREEN_WIDTH/2,PANEL_HEIGHT+GAME_AREA_HEIGHT/2+y_displacement))
    screen.blit(mesg,text_rect)

def get_random_food_position(snake_list): # Invariata
    while True:
        food_x=random.randrange(0,GRID_WIDTH); food_y=random.randrange(0,GRID_HEIGHT)
        if(food_x,food_y) not in snake_list: return(food_x,food_y)

def draw_button(text,font,text_color,rect,button_color,hover_color): # Invariata
    is_hovered=rect.collidepoint(pygame.mouse.get_pos())
    current_button_color=hover_color if is_hovered else button_color
    pygame.draw.rect(screen,current_button_color,rect,border_radius=10)
    text_surf=font.render(text,True,text_color)
    text_rect=text_surf.get_rect(center=rect.center)
    screen.blit(text_surf,text_rect)
    return is_hovered

def name_input_loop(achieved_score): # Invariata, usa UI_FPS
    global game_state,leaderboard_data,top_score_value
    user_name=""; input_box_rect=pygame.Rect(SCREEN_WIDTH//2-150,SCREEN_HEIGHT//2-25,300,50); running=True
    prompt_surf=menu_font_options.render("Nuovo High Score!",True,YELLOW)
    prompt_rect=prompt_surf.get_rect(center=(SCREEN_WIDTH//2,SCREEN_HEIGHT//2-140))
    instr_surf=font_style_panel.render("Inserisci il tuo nome (max 10 caratteri):",True,WHITE)
    instr_rect=instr_surf.get_rect(center=(SCREEN_WIDTH//2,SCREEN_HEIGHT//2-100))
    score_surf=font_style_panel.render(f"Punteggio: {achieved_score}",True,WHITE)
    score_rect=score_surf.get_rect(center=(SCREEN_WIDTH//2,SCREEN_HEIGHT//2-70))
    while running:
        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit();sys.exit()
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_RETURN:
                    final_name=user_name.strip();
                    if not final_name: final_name="Player"
                    add_entry_to_leaderboard(final_name,achieved_score); leaderboard_data=load_leaderboard()
                    if leaderboard_data: top_score_value=leaderboard_data[0]["score"]
                    game_state="LEADERBOARD"; running=False
                elif event.key==pygame.K_BACKSPACE: user_name=user_name[:-1]
                elif len(user_name)<MAX_NAME_LENGTH and(event.unicode.isalnum()or event.unicode==' '): user_name+=event.unicode
                if event.key==pygame.K_ESCAPE: game_state="MENU";running=False
        screen.fill(BLACK); screen.blit(prompt_surf,prompt_rect); screen.blit(instr_surf,instr_rect); screen.blit(score_surf,score_rect)
        pygame.draw.rect(screen,INPUT_BOX_COLOR_ACTIVE,input_box_rect,border_radius=5)
        text_surface=input_font.render(user_name,True,TEXT_INPUT_COLOR)
        screen.blit(text_surface,(input_box_rect.x+10,input_box_rect.y+(input_box_rect.height-text_surface.get_height())//2))
        pygame.draw.rect(screen,WHITE,input_box_rect,2,border_radius=5)
        pygame.display.flip(); clock.tick(UI_FPS)

def leaderboard_screen_loop(): # Invariata, usa UI_FPS
    global game_state,leaderboard_data
    running=True; back_button_rect=pygame.Rect(SCREEN_WIDTH//2-100,SCREEN_HEIGHT-80,200,50)
    while running:
        mouse_clicked_this_frame=False
        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit();sys.exit()
            if event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE: running=False;game_state="MENU"
            if event.type==pygame.MOUSEBUTTONDOWN and event.button==1: mouse_clicked_this_frame=True
        screen.fill(BLACK)
        title_surf=menu_font_title.render("Leaderboard",True,YELLOW)
        screen.blit(title_surf,title_surf.get_rect(center=(SCREEN_WIDTH//2,60)))
        if not leaderboard_data:
            no_scores_surf=menu_font_options.render("Nessun punteggio!",True,WHITE)
            screen.blit(no_scores_surf,no_scores_surf.get_rect(center=(SCREEN_WIDTH//2,SCREEN_HEIGHT//2-50)))
        else:
            y_offset=130
            for i,entry in enumerate(leaderboard_data):
                name_text=entry.get("name","N/A")[:MAX_NAME_LENGTH];score_text=str(entry.get("score",0))
                display_text=f"{i+1}. {name_text:<{MAX_NAME_LENGTH+1}} - {score_text:>5}"
                entry_surf=menu_font_options.render(display_text,True,MENU_TEXT_COLOR)
                screen.blit(entry_surf,entry_surf.get_rect(midleft=(SCREEN_WIDTH//2-200,y_offset+i*40)))
                if i>=MAX_LEADERBOARD_ENTRIES-1:break
        if draw_button("Indietro",menu_font_options,WHITE,back_button_rect,MENU_BUTTON_COLOR,MENU_BUTTON_HOVER_COLOR)and mouse_clicked_this_frame:
            running=False;game_state="MENU"
        pygame.display.flip();clock.tick(UI_FPS)

# --- MODIFICA: settings_screen_loop ora accetta is_modal ---
def settings_screen_loop(is_modal=False):
    global game_state, current_volume
    running = True
    volume_step = 0.1

    button_font = menu_font_options
    button_text_color = WHITE
    button_main_color = MENU_BUTTON_COLOR
    button_hover_color = MENU_BUTTON_HOVER_COLOR

    # Definisci le geometrie qui per averle disponibili per il disegno
    modal_bg_rect = None
    if is_modal:
        modal_width = SCREEN_WIDTH * 0.75 # Larghezza della finestra modale
        modal_height = GAME_AREA_HEIGHT * 0.7 # Altezza della finestra modale, un po' più alta
        modal_x = (SCREEN_WIDTH - modal_width) / 2
        modal_y = PANEL_HEIGHT + (GAME_AREA_HEIGHT - modal_height) / 2

        modal_bg_rect = pygame.Rect(modal_x, modal_y, modal_width, modal_height)

        title_rect_center_x = modal_bg_rect.centerx
        title_rect_top_y = modal_bg_rect.top + 40 # Un po' di spazio dall'alto

        volume_text_center_x = modal_bg_rect.centerx
        volume_text_center_y = title_rect_top_y + 80 # Spazio dal titolo

        vol_buttons_y_pos = volume_text_center_y + 50
        vol_button_size = 50
        vol_down_rect = pygame.Rect(modal_bg_rect.centerx - 100, vol_buttons_y_pos, vol_button_size, vol_button_size)
        vol_up_rect = pygame.Rect(modal_bg_rect.centerx + 50, vol_buttons_y_pos, vol_button_size, vol_button_size)
        
        back_button_rect = pygame.Rect(modal_bg_rect.centerx - 100, modal_bg_rect.bottom - 70, 200, 50)
        back_button_text = "OK"
    else: # Non modale
        title_rect_center_x = SCREEN_WIDTH // 2
        title_rect_top_y = 80

        volume_text_center_x = SCREEN_WIDTH // 2
        volume_text_center_y = 200
        
        vol_buttons_y_pos = 250
        vol_button_size = 50
        vol_down_rect = pygame.Rect(SCREEN_WIDTH // 2 - 125, vol_buttons_y_pos, vol_button_size, vol_button_size)
        vol_up_rect = pygame.Rect(SCREEN_WIDTH // 2 + 75, vol_buttons_y_pos, vol_button_size, vol_button_size)

        back_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 50)
        back_button_text = "Indietro"


    while running:
        mouse_clicked_this_frame = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    if not is_modal:
                        game_state = "MENU"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_clicked_this_frame = True

        if is_modal and modal_bg_rect is not None:
            pygame.draw.rect(screen, PANEL_COLOR, modal_bg_rect, border_radius=15)
            pygame.draw.rect(screen, WHITE, modal_bg_rect, 3, border_radius=15)
        elif not is_modal:
            screen.fill(BLACK)

        title_surf = menu_font_title.render("Impostazioni", True, YELLOW)
        screen.blit(title_surf, title_surf.get_rect(center=(title_rect_center_x, title_rect_top_y)))

        volume_text_surf = menu_font_options.render(f"Volume: {int(current_volume * 100)}%", True, MENU_TEXT_COLOR)
        screen.blit(volume_text_surf, volume_text_surf.get_rect(center=(volume_text_center_x, volume_text_center_y)))
        
        if draw_button("-", button_font, button_text_color, vol_down_rect, button_main_color, button_hover_color) and mouse_clicked_this_frame:
            current_volume = round(max(0.0, current_volume - volume_step), 1)
            if eat_sound: eat_sound.set_volume(current_volume)
            if game_over_sound: game_over_sound.set_volume(current_volume)
            # pygame.time.delay(100) # Non strettamente necessario qui se il click viene consumato
        
        if draw_button("+", button_font, button_text_color, vol_up_rect, button_main_color, button_hover_color) and mouse_clicked_this_frame:
            current_volume = round(min(1.0, current_volume + volume_step), 1)
            if eat_sound: eat_sound.set_volume(current_volume)
            if game_over_sound: game_over_sound.set_volume(current_volume)
            # pygame.time.delay(100)

        if draw_button(back_button_text, button_font, button_text_color, back_button_rect, button_main_color, button_hover_color) and mouse_clicked_this_frame:
            running = False
            if not is_modal:
                game_state = "MENU"
        
        pygame.display.flip()
        clock.tick(UI_FPS)

# --- NUOVA FUNZIONE: Menu di Pausa ---
def run_pause_menu():
    global game_state

    game_paused_surface = screen.copy()
    paused = True
    button_width = 300; button_height = 50; spacing = 15
    num_buttons = 4
    total_buttons_height = num_buttons * button_height + (num_buttons - 1) * spacing
    menu_block_start_y = PANEL_HEIGHT + (GAME_AREA_HEIGHT - total_buttons_height) / 2 + 50

    resume_rect = pygame.Rect(SCREEN_WIDTH//2-button_width//2, menu_block_start_y, button_width, button_height)
    settings_rect = pygame.Rect(SCREEN_WIDTH//2-button_width//2, menu_block_start_y + (button_height+spacing), button_width, button_height)
    main_menu_rect = pygame.Rect(SCREEN_WIDTH//2-button_width//2, menu_block_start_y + 2*(button_height+spacing), button_width, button_height)
    exit_game_rect = pygame.Rect(SCREEN_WIDTH//2-button_width//2, menu_block_start_y + 3*(button_height+spacing), button_width, button_height)

    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT - PANEL_HEIGHT), pygame.SRCALPHA)
    overlay.fill(PAUSE_OVERLAY_COLOR)
    action_taken = "RESUME"

    while paused:
        screen.blit(game_paused_surface, (0,0))
        screen.blit(overlay, (0, PANEL_HEIGHT))
        pause_title_surf = menu_font_title.render("Pausa", True, YELLOW)
        pause_title_rect = pause_title_surf.get_rect(center=(SCREEN_WIDTH // 2, PANEL_HEIGHT + GAME_AREA_HEIGHT // 2 - 120 ))
        screen.blit(pause_title_surf, pause_title_rect)

        mouse_clicked_this_frame = False # Resetta ad ogni iterazione del loop di pausa
        for event in pygame.event.get():
            if event.type == pygame.QUIT: action_taken = "EXIT_GAME"; paused = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: action_taken = "RESUME"; paused = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_clicked_this_frame = True # Imposta solo se C'È un evento MOUSEBUTTONDOWN
        
        if draw_button("Riprendi", pause_menu_font, MENU_TEXT_COLOR, resume_rect, MENU_BUTTON_COLOR, MENU_BUTTON_HOVER_COLOR) and mouse_clicked_this_frame:
            action_taken = "RESUME"; paused = False
        
        elif draw_button("Impostazioni", pause_menu_font, MENU_TEXT_COLOR, settings_rect, MENU_BUTTON_COLOR, MENU_BUTTON_HOVER_COLOR) and mouse_clicked_this_frame:
            settings_screen_loop(is_modal=True)
            # --- MODIFICA CRUCIALE: Consuma eventi del mouse dopo il ritorno dalla modale ---
            pygame.event.get(eventtype=[pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP]) # Svuota la coda da eventi mouse
            mouse_clicked_this_frame = False # Assicura che il click non venga riprocessato subito
            # Dopo il ritorno da settings, il loop di pausa continua, ridisegnando il menu di pausa.
            # game_paused_surface non viene ricatturato qui; se le impostazioni cambiassero
            # qualcosa di visivo nel gioco (non solo volume), bisognerebbe pensare a come aggiornarlo.

        elif draw_button("Menu Principale", pause_menu_font, MENU_TEXT_COLOR, main_menu_rect, MENU_BUTTON_COLOR, MENU_BUTTON_HOVER_COLOR) and mouse_clicked_this_frame:
            action_taken = "GOTO_MAIN_MENU"; paused = False
        
        elif draw_button("Esci dal Gioco", pause_menu_font, MENU_TEXT_COLOR, exit_game_rect, MENU_BUTTON_COLOR, MENU_BUTTON_HOVER_COLOR) and mouse_clicked_this_frame:
            action_taken = "EXIT_GAME"; paused = False

        pygame.display.flip()
        clock.tick(UI_FPS)
    
    return action_taken


# --- Ciclo di Gioco (MODIFICATO per menu di pausa) ---
def game_loop():
    global top_score_value, game_state, leaderboard_data, current_score_for_name_entry
    current_game_fps = INITIAL_FPS
    game_over_flag = False; game_close_screen = False
    snake_head_pos = [GRID_WIDTH//2,GRID_HEIGHT//2]; snake_list=[list(snake_head_pos)]; snake_length=1
    current_direction=RIGHT; change_to_direction=current_direction
    food_pos=get_random_food_position(snake_list); score=0
    first_game_over_sound_played=False

    while not game_over_flag: # Loop principale della partita
        # ... (logica game_close_screen invariata) ...
        while game_close_screen:
            if not first_game_over_sound_played:
                if game_over_sound: game_over_sound.play()
                first_game_over_sound_played = True
                if check_if_qualifies(score, leaderboard_data):
                    current_score_for_name_entry = score; game_state = "ENTER_NAME"
                    game_close_screen = False; game_over_flag = True; break
            screen.fill(BLACK)
            current_top_s = leaderboard_data[0]["score"] if leaderboard_data else 0
            display_score_and_highscore_panel(score, current_top_s)
            display_message_game_area("Hai perso!",RED,-70,chosen_font=game_over_font_big)
            display_message_game_area(f"Punteggio: {score}",BLUE,-20,chosen_font=game_over_font_small)
            display_message_game_area("Premi 'R' per Riprovare",WHITE,60,chosen_font=game_over_font_small)
            display_message_game_area("'M' per Menu Principale",WHITE,100,chosen_font=game_over_font_small)
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_m: game_close_screen=False;game_over_flag=True;game_state="MENU"
                    if event.key == pygame.K_r:
                        game_close_screen=False;game_over_flag=False
                        snake_head_pos=[GRID_WIDTH//2,GRID_HEIGHT//2];snake_list=[list(snake_head_pos)];snake_length=1
                        current_direction=RIGHT;change_to_direction=current_direction
                        food_pos=get_random_food_position(snake_list);score=0
                        first_game_over_sound_played=False;current_game_fps=INITIAL_FPS
                        break
            if not game_close_screen: break
        if game_over_flag: break

        # Eventi di gioco normale
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: # Gestione ESC per Pausa
                    
                    # Cattura lo schermo attuale PRIMA di disegnare il menu di pausa
                    # game_paused_surface = screen.copy() # Questo è meglio farlo DENTRO run_pause_menu

                    pause_action = run_pause_menu() # Chiama il menu di pausa
                    
                    if pause_action == "GOTO_MAIN_MENU":
                        game_over_flag = True; game_state = "MENU"
                    elif pause_action == "EXIT_GAME":
                        pygame.quit(); sys.exit()
                    # Se "RESUME", non fa nulla qui, il gioco continuerà
                    # È importante che run_pause_menu() ridisegni lo schermo con flip()
                    # e che il game_loop continui e ridisegni lo stato del gioco.
                    # Potrebbe essere necessario un refresh esplicito dello schermo di gioco qui
                    # se run_pause_menu non lo lascia "pulito".
                    # Il modo in cui run_pause_menu ora cattura e ridisegna lo sfondo dovrebbe andare bene.
                    break # Esce dal loop eventi per questo frame per evitare che l'ESC venga processato di nuovo
                
                elif event.key == pygame.K_a and current_direction != RIGHT: change_to_direction=LEFT
                elif event.key == pygame.K_d and current_direction != LEFT: change_to_direction=RIGHT
                elif event.key == pygame.K_w and current_direction != DOWN: change_to_direction=UP
                elif event.key == pygame.K_s and current_direction != UP: change_to_direction=DOWN
        
        if game_over_flag: break # Se il menu di pausa ha deciso di uscire al menu principale

        # ... (resto del game_loop invariato) ...
        current_direction=change_to_direction
        snake_head_pos[0]+=current_direction[0]; snake_head_pos[1]+=current_direction[1]
        if not (0<=snake_head_pos[0]<GRID_WIDTH and 0<=snake_head_pos[1]<GRID_HEIGHT): game_close_screen=True
        if list(snake_head_pos) in snake_list[:-1]: game_close_screen=True
        if game_close_screen: continue

        snake_list.append(list(snake_head_pos))
        if len(snake_list)>snake_length: del snake_list[0]
        if snake_head_pos[0]==food_pos[0] and snake_head_pos[1]==food_pos[1]:
            food_pos=get_random_food_position(snake_list); snake_length+=1; score+=10
            if eat_sound: eat_sound.play()
            if current_game_fps < MAX_FPS:
                current_game_fps += FPS_INCREMENT_PER_FOOD
                current_game_fps = min(current_game_fps, MAX_FPS)
        screen.fill(BLACK) # Pulisce l'area di gioco
        current_top_s = leaderboard_data[0]["score"] if leaderboard_data else 0
        display_score_and_highscore_panel(score, current_top_s) # Ridisegna il pannello punteggi
        draw_snake(snake_list); draw_food(food_pos) # Ridisegna gli elementi di gioco
        pygame.display.update(); clock.tick(current_game_fps)

# Menu Principale (invariato, usa UI_FPS)
def main_menu_loop():
    global game_state
    button_width=300; button_height=60; spacing=20; start_y=200
    new_game_rect=pygame.Rect(SCREEN_WIDTH//2-button_width//2,start_y,button_width,button_height)
    leaderboard_rect=pygame.Rect(SCREEN_WIDTH//2-button_width//2,start_y+(button_height+spacing),button_width,button_height)
    settings_rect=pygame.Rect(SCREEN_WIDTH//2-button_width//2,start_y+2*(button_height+spacing),button_width,button_height)
    exit_rect=pygame.Rect(SCREEN_WIDTH//2-button_width//2,start_y+3*(button_height+spacing),button_width,button_height)
    menu_running=True
    while menu_running:
        mouse_clicked_this_frame=False
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: mouse_clicked_this_frame = True
        screen.fill(BLACK)
        title_surf = menu_font_title.render("Snake Game", True, GREEN)
        screen.blit(title_surf, title_surf.get_rect(center=(SCREEN_WIDTH // 2, 100)))
        if draw_button("Nuova Partita", menu_font_options, MENU_TEXT_COLOR, new_game_rect, MENU_BUTTON_COLOR, MENU_BUTTON_HOVER_COLOR) and mouse_clicked_this_frame:
            game_state = "GAME"; menu_running = False
        if draw_button("Leaderboard", menu_font_options, MENU_TEXT_COLOR, leaderboard_rect, MENU_BUTTON_COLOR, MENU_BUTTON_HOVER_COLOR) and mouse_clicked_this_frame:
            leaderboard_data = load_leaderboard(); game_state = "LEADERBOARD"; menu_running = False
        if draw_button("Impostazioni", menu_font_options, MENU_TEXT_COLOR, settings_rect, MENU_BUTTON_COLOR, MENU_BUTTON_HOVER_COLOR) and mouse_clicked_this_frame:
            game_state = "SETTINGS"; menu_running = False # settings_screen_loop gestirà il ritorno a "MENU"
        if draw_button("Esci", menu_font_options, MENU_TEXT_COLOR, exit_rect, MENU_BUTTON_COLOR, MENU_BUTTON_HOVER_COLOR) and mouse_clicked_this_frame:
            pygame.quit(); sys.exit()
        pygame.display.flip(); clock.tick(UI_FPS)

# Avvio del gioco (Loop Principale dell'Applicazione)
if __name__ == '__main__':
    load_sounds()
    leaderboard_data = load_leaderboard()
    if leaderboard_data: top_score_value = leaderboard_data[0]["score"]
    else: top_score_value = 0

    while True:
        if game_state == "MENU": main_menu_loop()
        elif game_state == "GAME": game_loop()
        elif game_state == "LEADERBOARD": leaderboard_screen_loop()
        elif game_state == "SETTINGS": settings_screen_loop(is_modal=False) # Chiamata non modale
        elif game_state == "ENTER_NAME": name_input_loop(current_score_for_name_entry)