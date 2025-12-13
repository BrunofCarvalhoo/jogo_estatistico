import pygame
import random
import math
import time
import json # Para salvar o ranking

pygame.init()
pygame.font.init()


WIDTH, HEIGHT = 1200, 700
GAME_WIDTH = 800
STATS_WIDTH = 400

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jogo da Distribuição de Probabilidade - Estilo 'The Wall'")
clock = pygame.time.Clock()

# --- Cores ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (230, 230, 230)
BLUE = (30, 144, 255)
RED = (255, 69, 0)
GREEN = (40, 190, 40)
GOLD = (255, 215, 0) # Cor amarela para perguntas
BG_COLOR = (20, 20, 40) 
PEG_COLOR = (150, 150, 170)

# --- Fontes ---
TITLE_FONT = pygame.font.SysFont('Arial', 30, bold=True)
STATS_FONT = pygame.font.SysFont('Arial', 22)
SMALL_FONT = pygame.font.SysFont('Arial', 16)
VALUE_FONT = pygame.font.SysFont('Arial', 18, bold=True)
SCORE_FONT = pygame.font.SysFont('Impact', 60)
FLOATING_FONT = pygame.font.SysFont('Arial', 24, bold=True)
QUESTION_FONT = pygame.font.SysFont('Arial', 26, bold=True)
OPTION_FONT = pygame.font.SysFont('Arial', 22)
INPUT_FONT = pygame.font.SysFont('Arial', 40)
RANKING_FONT = pygame.font.SysFont('Arial', 28)
MENU_TITLE_FONT = pygame.font.SysFont('Impact', 70) # Fonte para o menu
MENU_OPTION_FONT = pygame.font.SysFont('Arial', 40, bold=True) # Fonte das opções

# --- Constantes do Jogo ---
ROWS = 12
BINS = ROWS + 1 
PEG_WIDTH = 10
PEG_HEIGHT = 10
BALL_RADIUS = 8
START_Y = 50

BIN_WIDTH = GAME_WIDTH / BINS 
PEG_H_SPACING = BIN_WIDTH 
PEG_V_SPACING = 45 

BIN_VALUES = [
    2000, 200, 1000, 10000, 500, 1, 30, 1, 500, 10000, 1000, 200, 2000
]
RANKING_FILE = "ranking.json"

# --- Retângulos dos botões do menu ---
MENU_JOGAR_RECT = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 30, 300, 70)
MENU_RANKING_RECT = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 60, 300, 70)
MENU_TESTES_RECT = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 150, 300, 70) 


# --- Variáveis de Jogo ---
bin_counts = [0] * BINS
total_balls = 0
total_score = 0 
balls = [] 
pegs = [] 
floating_scores = []
option_rects = [] 

questions = [
    {
        "question": "Qual é a capital do estado do Amazonas?",
        "options": ["Manaus", "Belém", "Rio Branco", "Porto Velho"],
        "correct": 0
    },
    {
        "question": "Qual estado brasileiro é conhecido como a 'Terra da Garoa'?",
        "options": ["Rio de Janeiro", "Minas Gerais", "São Paulo", "Paraná"],
        "correct": 2
    },
    {
        "question": "Onde estão localizadas as Cataratas do Iguaçu?",
        "options": ["Santa Catarina", "Paraná", "Mato Grosso do Sul", "Rio Grande do Sul"],
        "correct": 1
    },
    {
        "question": "Qual é o maior estado do Brasil em área territorial?",
        "options": ["Minas Gerais", "Bahia", "Pará", "Amazonas"],
        "correct": 3
    },
    {
        "question": "Qual destes estados NÃO faz parte da Região Nordeste?",
        "options": ["Bahia", "Ceará", "Maranhão", "Espírito Santo"],
        "correct": 3
    },
    {
        "question": "Quanto é 7 x 8?",
        "options": ["54", "56", "63", "49"],
        "correct": 1
    },
    {
        "question": "Qual é a raiz quadrada de 144?",
        "options": ["11", "13", "14", "12"],
        "correct": 3
    },
    {
        "question": "Quanto é 15% de 200?",
        "options": ["30", "20", "25", "35"],
        "correct": 0
    },
    {
        "question": "Quanto é 9 + 10 x 2?",
        "options": ["38", "21", "29", "40"],
        "correct": 2 # (10*2 = 20, 20+9 = 29)
    },
    {
        "question": "Qual é o próximo número na sequência: 2, 5, 8, 11, ...?",
        "options": ["12", "13", "14", "15"],
        "correct": 2 # (Soma 3)
    }
]
random.shuffle(questions)

# --- Estado do Jogo ---
game_state = "MAIN_MENU" 
current_question_index = 0
player_name = "" 
current_slot = BINS // 2
last_answer_correct = None
ranking_data = [] 

# --- FUNÇÕES DE RANKING ---
def load_ranking():
    global ranking_data
    try:
        with open(RANKING_FILE, 'r') as f:
            ranking_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        ranking_data = []

def save_ranking(name, score):
    global ranking_data
    ranking_data.append({"name": name, "score": score})
    ranking_data = sorted(ranking_data, key=lambda x: x['score'], reverse=True)
    ranking_data = ranking_data[:10]
    
    with open(RANKING_FILE, 'w') as f:
        json.dump(ranking_data, f, indent=4)

# --- TELA DE NOME ---
def draw_name_input():
    # Overlay escuro
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(200) 
    overlay.fill(BG_COLOR)
    screen.blit(overlay, (0, 0))
    
    draw_text("Digite seu nome:", TITLE_FONT, GOLD, WIDTH // 2, HEIGHT // 2 - 100, center=True)
    
    input_box = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 - 40, 400, 80)
    pygame.draw.rect(screen, WHITE, input_box, border_radius=10)
    pygame.draw.rect(screen, GOLD, input_box, 3, border_radius=10)
    
    draw_text(player_name, INPUT_FONT, BLACK, input_box.centerx, input_box.centery, center=True, center_y=True)
    
    draw_text("Pressione ENTER para começar", STATS_FONT, WHITE, WIDTH // 2, HEIGHT // 2 + 80, center=True)
    draw_text("Pressione ESC para voltar ao Menu", SMALL_FONT, GRAY, WIDTH // 2, HEIGHT // 2 + 120, center=True) 

#  --- TELA DE MENU PRINCIPAL ---
def draw_main_menu():
    screen.fill(BG_COLOR) # Fundo sólido para o menu
    
    draw_text("THE PROBABILITY WALL", MENU_TITLE_FONT, GOLD, WIDTH // 2, HEIGHT // 3, center=True, center_y=True)

    pos = pygame.mouse.get_pos()
    
    # Botão Jogar
    if MENU_JOGAR_RECT.collidepoint(pos):
        pygame.draw.rect(screen, GOLD, MENU_JOGAR_RECT, border_radius=10)
        draw_text("JOGAR", MENU_OPTION_FONT, BLACK, MENU_JOGAR_RECT.centerx, MENU_JOGAR_RECT.centery, center=True, center_y=True)
    else:
        pygame.draw.rect(screen, BLUE, MENU_JOGAR_RECT, border_radius=10)
        pygame.draw.rect(screen, WHITE, MENU_JOGAR_RECT, 3, border_radius=10)
        draw_text("JOGAR", MENU_OPTION_FONT, WHITE, MENU_JOGAR_RECT.centerx, MENU_JOGAR_RECT.centery, center=True, center_y=True)
        
    # Botão Ranking
    if MENU_RANKING_RECT.collidepoint(pos):
        pygame.draw.rect(screen, GOLD, MENU_RANKING_RECT, border_radius=10)
        draw_text("RANKING", MENU_OPTION_FONT, BLACK, MENU_RANKING_RECT.centerx, MENU_RANKING_RECT.centery, center=True, center_y=True)
    else:
        pygame.draw.rect(screen, BLUE, MENU_RANKING_RECT, border_radius=10)
        pygame.draw.rect(screen, WHITE, MENU_RANKING_RECT, 3, border_radius=10)
        draw_text("RANKING", MENU_OPTION_FONT, WHITE, MENU_RANKING_RECT.centerx, MENU_RANKING_RECT.centery, center=True, center_y=True)

    # Botão Testes
    if MENU_TESTES_RECT.collidepoint(pos):
        pygame.draw.rect(screen, GOLD, MENU_TESTES_RECT, border_radius=10)
        draw_text("TESTES", MENU_OPTION_FONT, BLACK, MENU_TESTES_RECT.centerx, MENU_TESTES_RECT.centery, center=True, center_y=True)
    else:
        pygame.draw.rect(screen, BLUE, MENU_TESTES_RECT, border_radius=10)
        pygame.draw.rect(screen, WHITE, MENU_TESTES_RECT, 3, border_radius=10)
        draw_text("TESTES", MENU_OPTION_FONT, WHITE, MENU_TESTES_RECT.centerx, MENU_TESTES_RECT.centery, center=True, center_y=True)


# --- TELA DE RANKING ---
def draw_ranking_screen():
    screen.fill(BG_COLOR)
    
    draw_text("Ranking - Top 10", TITLE_FONT, GOLD, WIDTH // 2, 100, center=True)
    
    y_start = 180
    if not ranking_data:
         draw_text("Nenhum ranking salvo ainda.", RANKING_FONT, WHITE, WIDTH // 2, 300, center=True)
            
    for i, entry in enumerate(ranking_data):
        rank = f"{i+1}."
        name = entry['name']
        score = f"R$ {entry['score']:,}"
        
        color = WHITE
        if game_state == "RANKING" and entry['name'] == player_name and entry['score'] == total_score:
            color = GOLD 
        
        draw_text(rank, RANKING_FONT, color, WIDTH // 2 - 250, y_start + i * 45)
        draw_text(name, RANKING_FONT, color, WIDTH // 2 - 200, y_start + i * 45)
        draw_text(score, RANKING_FONT, color, WIDTH // 2 + 100, y_start + i * 45)


#  ADICIONA BOLAS DE TESTE
def add_test_balls(count):
    
    x_pos = (current_slot * BIN_WIDTH) + (BIN_WIDTH / 2)
    # is_correct=True para bolas verdes
    for _ in range(count):
        balls.append(Ball(is_correct=True, x_start=x_pos))


def calculate_theoretical_dist(n, total):
    if total == 0:
        return [0] * (n + 1)
    
    probs = []
    for k in range(n + 1):
        prob_k = math.comb(n, k) / (2**n)
        probs.append(prob_k * total)
    return probs

def draw_text(text, font, color, x, y, center=False, center_y=False):
    surface = font.render(text, True, color)
    rect = surface.get_rect()
    if center:
        rect.centerx = x
    else:
        rect.x = x
    if center_y:
        rect.centery = y
    else:
        rect.y = y
    if center and center_y:
        rect.center = (x, y)
    screen.blit(surface, rect)


class FloatingScore:
    def __init__(self, x, y, value, is_correct):
        self.x = x
        self.y = y
        self.value = value
        self.is_correct = is_correct 
        self.alpha = 255 
        self.vy = -2    

    def update(self):
        self.y += self.vy
        self.alpha -= 5 
        if self.alpha < 0:
            self.alpha = 0

    def draw(self):
        if self.alpha > 0:
            text = ""
            color = WHITE
            
            if self.is_correct:
                color = GREEN if self.value > 10 else WHITE 
                if self.value >= 1000: color = GOLD
                text = f"+ R$ {self.value:,}"
            else:
                color = RED
                text = f"- R$ {self.value:,}"
                
            s = FLOATING_FONT.render(text, True, color)
            s.set_alpha(self.alpha)
            screen.blit(s, (self.x - s.get_width() // 2, self.y - s.get_height() // 2))


class Ball:
    def __init__(self, is_correct, x_start):
        self.x = x_start
        self.y = START_Y
        self.vy = 0
        self.vx = 0
        self.current_row = 0 
        self.target_peg_y = pegs[0][0][1] 
        self.active = True
        self.is_correct = is_correct 
        self.color = GREEN if is_correct else RED 

    def update(self):
        if not self.active:
            return

        self.vy += 0.5
        self.y += self.vy
        self.x += self.vx

        # --- Lógica das paredes laterais ---
        if self.x - BALL_RADIUS < 0:
            self.x = BALL_RADIUS
            self.vx *= -0.5 
        
        if self.x + BALL_RADIUS > GAME_WIDTH - 2:
            self.x = GAME_WIDTH - BALL_RADIUS - 2
            self.vx *= -0.5
        
        if self.current_row < ROWS and self.y >= self.target_peg_y:
            self.y = self.target_peg_y 
            
            self.vx = random.choice([-1, 1]) * 2.5 
            self.vy = -1
            
            self.current_row += 1  
            
            if self.current_row < ROWS:
                self.target_peg_y = pegs[self.current_row][0][1] 
            
        
        elif self.current_row == ROWS and self.y > pegs[-1][0][1] + PEG_V_SPACING:
            # Se passou da última fileira de pinos
            self.vy = 5 
            self.vx = 0 
            
            
            bin_base_y = HEIGHT - 80 
            if self.y >= bin_base_y:
                self.y = bin_base_y
                self.active = False 
                
                
                bin_width = GAME_WIDTH / BINS
                bin_index = int(self.x / bin_width)
                if bin_index < 0: bin_index = 0
                if bin_index >= BINS: bin_index = BINS - 1
                
                
                global total_balls, total_score
                bin_counts[bin_index] += 1
                total_balls += 1
                
                
                value_won = BIN_VALUES[bin_index]
                
                # A pontuação só é afetada se NÃO estivermos no modo de teste
                if game_state != "TEST_MENU":
                    if self.is_correct:
                        total_score += value_won
                        floating_scores.append(FloatingScore(self.x, self.y - 20, value_won, is_correct=True))
                    else:
                        total_score -= value_won
                        floating_scores.append(FloatingScore(self.x, self.y - 20, value_won, is_correct=False))


    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), BALL_RADIUS)
        pygame.draw.circle(screen, WHITE, (int(self.x) - 2, int(self.y) - 2), int(BALL_RADIUS // 2.5))


def draw_question_panel():
    global option_rects
    option_rects.clear()
    
    overlay = pygame.Surface((GAME_WIDTH, HEIGHT))
    overlay.set_alpha(200) 
    overlay.fill(BG_COLOR)
    screen.blit(overlay, (0, 0))
    
    
    # Aumentei a largura (de 500 para 550) e altura (de 400 para 450)
    box_width = GAME_WIDTH // 2 + 150
    box_height = HEIGHT // 2 + 100
    box_x = (GAME_WIDTH - box_width) // 2
    box_y = (HEIGHT - box_height) // 2 - 25 # Um pouco mais para cima
    
    box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
    pygame.draw.rect(screen, LIGHT_GRAY, box_rect, border_radius=15)
    pygame.draw.rect(screen, BLUE, box_rect, 5, border_radius=15)
    
    if current_question_index < len(questions):
        current_q = questions[current_question_index]
        
        # --- INÍCIO DA LÓGICA DE QUEBRA DE LINHA (WORD-WRAP) ---
        question_text = current_q["question"]
        words = question_text.split(' ')
        lines = []
        current_line = ""
        
        # Margem de 40px (20 de cada lado)
        max_width = box_rect.width - 40 
        
        for word in words:
            # Testa a largura da linha com a nova palavra
            test_line = current_line + word + " "
            try:
                line_surface = QUESTION_FONT.render(test_line, True, BLACK)
                line_width = line_surface.get_width()
            except pygame.error:
                line_width = max_width # Evita erro se a fonte não puder renderizar
        
            if line_width <= max_width:
                # Palavra cabe, continua na linha
                current_line = test_line
            else:
                # Palavra não cabe, finaliza a linha anterior (sem espaço extra)
                lines.append(current_line.strip())
                # Começa uma nova linha com a palavra atual
                current_line = word + " "
        
        # Adiciona a última linha
        lines.append(current_line.strip())
        
        # Desenha as linhas quebadas
        current_y = box_rect.y + 30 # Y inicial (com uma margem de 30px)
        line_height = QUESTION_FONT.get_linesize() # Pega a altura da fonte
        
        for line in lines:
            draw_text(line, QUESTION_FONT, BLACK, box_rect.centerx, current_y, center=True)
            current_y += line_height # Move para a próxima linha
        # --- FIM DA LÓGICA DE QUEBRA DE LINHA ---

        # --- Opções ---
        # Y fixo para as opções, dando 150px de espaço para a pergunta (de 30 até 180)
        option_y_start = box_rect.y + 150 
        
        # Calcula a altura de cada opção com base no espaço restante
        available_height_for_options = (box_rect.y + box_rect.height) - option_y_start - 20 # 20px margem inferior
        option_height = (available_height_for_options / 4) - 10 # -10 para dar espaço entre elas
        
        if option_height > 70: # Limita a altura máxima da opção
            option_height = 70
        elif option_height < 40: # Limite mínimo
             option_height = 40

        for i, option in enumerate(current_q["options"]):
            option_text = f"{i+1}. {option}"
            
            # Recalcula a altura da caixa da opção
            option_box_y = option_y_start + i * (option_height + 10) # 10px de espaço
            
            option_box = pygame.Rect(box_rect.x + 30, option_box_y, box_rect.width - 60, option_height)
            option_rects.append(option_box)
            
            pos = pygame.mouse.get_pos()
            if option_box.collidepoint(pos):
                pygame.draw.rect(screen, GRAY, option_box, border_radius=10)
            else:
                pygame.draw.rect(screen, WHITE, option_box, border_radius=10)
                
            pygame.draw.rect(screen, BLACK, option_box, 2, border_radius=10)
            
            draw_text(option_text, OPTION_FONT, BLACK, option_box.x + 15, option_box.centery, center_y=True)
    else:
        draw_text("Calculando pontuação final...", TITLE_FONT, BLACK, box_rect.centerx, box_rect.centery, center=True, center_y=True)

# --- Desenha o seletor de posição da bola ---
def draw_slot_selector():
    slot_x = (current_slot * BIN_WIDTH) + (BIN_WIDTH / 2)
    
    points = [
        (slot_x, START_Y - 10),    
        (slot_x - 10, START_Y - 25), 
        (slot_x + 10, START_Y - 25)  
    ]
    
    
    color = RED if last_answer_correct is False else GREEN
    pygame.draw.polygon(screen, color, points)
    

def setup_board():
    pegs.clear()
    
    num_cols = BINS 
    col_width = GAME_WIDTH / num_cols 
    
    for r in range(ROWS):
        row_pegs = []
        peg_y = START_Y + 100 + r * PEG_V_SPACING
        
        is_staggered_row = (r % 2 == 1)
        
        if is_staggered_row:
            num_pegs_in_row = num_cols - 1
            start_x = col_width 
        else:
            num_pegs_in_row = num_cols
            start_x = col_width / 2
            
        for i in range(num_pegs_in_row):
            peg_x = start_x + i * col_width
            row_pegs.append((int(peg_x), int(peg_y)))
        pegs.append(row_pegs)

def draw_board():
    # --- Desenha retângulos em vez de círculos ---
    for row in pegs:
        for pos in row:
            peg_rect = pygame.Rect(
                pos[0] - PEG_WIDTH // 2, 
                pos[1] - PEG_HEIGHT // 2, 
                PEG_WIDTH, 
                PEG_HEIGHT
            )
            pygame.draw.rect(screen, PEG_COLOR, peg_rect)
            
    bin_base_y = HEIGHT - 80
    
    # --- Desenhar paredes laterais ---
    pygame.draw.line(screen, PEG_COLOR, (0, START_Y + 20), (0, bin_base_y), 3)
    pygame.draw.line(screen, PEG_COLOR, (GAME_WIDTH - 2, START_Y + 20), (GAME_WIDTH - 2, bin_base_y), 3)
    
    
    for i in range(BINS + 1): 
        line_x = i * BIN_WIDTH
        if i == BINS: 
            line_x -= 2 
        pygame.draw.line(screen, PEG_COLOR, (line_x, bin_base_y), (line_x, HEIGHT), 3)

    
    for i in range(BINS): 
        text_x_center = (i * BIN_WIDTH) + (BIN_WIDTH / 2)
        
        value_text = f"R${BIN_VALUES[i]}"
        if BIN_VALUES[i] >= 1000:
             value_text = f"R${BIN_VALUES[i]//1000}k" 
        if BIN_VALUES[i] == 1:
            value_text = "R$ 1"
            
        color = GOLD if BIN_VALUES[i] >= 1000 else WHITE
        draw_text(value_text, VALUE_FONT, color, text_x_center, bin_base_y + 40, center=True, center_y=True)

    pygame.draw.rect(screen, PEG_COLOR, (0, bin_base_y, GAME_WIDTH, 10))


def draw_stats_panel():
    pygame.draw.rect(screen, LIGHT_GRAY, (GAME_WIDTH, 0, STATS_WIDTH, HEIGHT))
    pygame.draw.line(screen, GRAY, (GAME_WIDTH, 0), (GAME_WIDTH, HEIGHT), 2)
    
    draw_text("Análise de Probabilidade", TITLE_FONT, BLACK, GAME_WIDTH + STATS_WIDTH / 2, 20, center=True)
    draw_text(f"Total de Bolas: {total_balls}", STATS_FONT, BLACK, GAME_WIDTH + 20, 80)
    
    chart_x = GAME_WIDTH + 40
    chart_y_emp = 350 
    chart_y_teo = 610 
    chart_height = 180
    bar_width = (STATS_WIDTH - 80) / BINS
    
    theoretical_counts = calculate_theoretical_dist(ROWS, total_balls)
    
    if total_balls > 0:
        max_emp_count = max(bin_counts)
        max_teo_count = max(theoretical_counts)
        global_max_count = max(max_emp_count, max_teo_count, 1)

        draw_text("Distribuição Empírica (Frequência):", STATS_FONT, BLACK, GAME_WIDTH + 20, 140)
        for i, count in enumerate(bin_counts):
            bar_h = (count / global_max_count) * chart_height
            bar_rect = pygame.Rect(chart_x + i * bar_width, chart_y_emp - bar_h, bar_width - 2, bar_h)
            pygame.draw.rect(screen, BLUE, bar_rect)
            
            count_text = SMALL_FONT.render(str(count), True, BLACK)
            screen.blit(count_text, (bar_rect.centerx - count_text.get_width() / 2, bar_rect.bottom + 5))
        pygame.draw.line(screen, BLACK, (chart_x - 5, chart_y_emp), (chart_x + bar_width * BINS, chart_y_emp), 2)

        draw_text("Distribuição Teórica (Binomial):", STATS_FONT, BLACK, GAME_WIDTH + 20, 400)
        points = []
        for i, theo_count in enumerate(theoretical_counts):
            bar_h = (theo_count / global_max_count) * chart_height
            point_x = chart_x + (i + 0.5) * bar_width
            point_y = chart_y_teo - bar_h
            points.append((point_x, point_y))
        if len(points) > 1:
            pygame.draw.lines(screen, RED, False, points, 3)
        pygame.draw.line(screen, BLACK, (chart_x - 5, chart_y_teo), (chart_x + bar_width * BINS, chart_y_teo), 2)
    else:
        draw_text("Distribuição Empírica (Frequência):", STATS_FONT, BLACK, GAME_WIDTH + 20, 140)
        pygame.draw.line(screen, BLACK, (chart_x - 5, chart_y_emp), (chart_x + bar_width * BINS, chart_y_emp), 2)
        draw_text("Distribuição Teórica (Binomial):", STATS_FONT, BLACK, GAME_WIDTH + 20, 400)
        pygame.draw.line(screen, BLACK, (chart_x - 5, chart_y_teo), (chart_x + bar_width * BINS, chart_y_teo), 2)


#--- Função de Reset do Teste ---
def reset_test_board():
    global bin_counts, total_balls, total_score, game_state, current_slot 
    bin_counts = [0] * BINS
    total_balls = 0
    # Zeramos o score no modo teste
    total_score = 0 
    balls.clear()
    floating_scores.clear()
    current_slot = BINS // 2 
    game_state = "TEST_MENU"


#--- Função de Reset do Jogo ---
def reset_game():
    global bin_counts, total_balls, total_score, current_question_index, player_name, game_state, current_slot
    bin_counts = [0] * BINS
    total_balls = 0
    total_score = 0
    balls.clear()
    floating_scores.clear()
    current_question_index = 0
    player_name = "" 
    current_slot = BINS // 2 # Reseta o slot aqui também
    game_state = "NAME_INPUT" 
    random.shuffle(questions)
    load_ranking() 


# --- Início do Jogo ---
running = True
setup_board() 
load_ranking() 

# --- LOOP PRINCIPAL ---
while running:
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        # --- Lógica de Teclado (KEYDOWN) ---
        if event.type == pygame.KEYDOWN:
            
            if game_state == "MENU_RANKING":
                if event.key == pygame.K_ESCAPE: 
                    game_state = "MAIN_MENU"

            elif game_state == "NAME_INPUT":
                if event.key == pygame.K_RETURN: 
                    if player_name.strip():
                        game_state = "ASKING"
                elif event.key == pygame.K_BACKSPACE: 
                    player_name = player_name[:-1]
                elif event.key == pygame.K_ESCAPE: 
                    game_state = "MAIN_MENU"
                    player_name = "" 
                else:
                    if len(player_name) < 15:
                        player_name += event.unicode
            
            elif game_state == "SELECT_SLOT":
                if event.key == pygame.K_LEFT:
                    current_slot = max(0, current_slot - 1) 
                elif event.key == pygame.K_RIGHT:
                    current_slot = min(BINS - 1, current_slot + 1) 
                elif event.key == pygame.K_SPACE:
                    x_pos = (current_slot * BIN_WIDTH) + (BIN_WIDTH / 2)
                    balls.append(Ball(is_correct=last_answer_correct, x_start=x_pos))
                    
                    last_answer_correct = None 
                    game_state = "DROPPING" 

            elif game_state == "RANKING": 
                if event.key == pygame.K_r: 
                    reset_game() 
            
            elif game_state in ["ASKING", "DROPPING", "SELECT_SLOT"]:
                if event.key == pygame.K_r: 
                    reset_game() 
            
            elif game_state == "TEST_MENU":
                if event.key == pygame.K_SPACE:
                    add_test_balls(1)
                elif event.key == pygame.K_a:
                    add_test_balls(3)
                # ### NOVO: Mover o seletor ###
                elif event.key == pygame.K_LEFT:
                    current_slot = max(0, current_slot - 1) 
                elif event.key == pygame.K_RIGHT:
                    current_slot = min(BINS - 1, current_slot + 1) 
                elif event.key == pygame.K_ESCAPE: 
                    game_state = "MAIN_MENU"
                elif event.key == pygame.K_r:
                    reset_test_board() 
            

        # --- Lógica de Clique do Mouse ---
        if event.type == pygame.MOUSEBUTTONDOWN:
            
            if game_state == "MAIN_MENU":
                pos = pygame.mouse.get_pos()
                if MENU_JOGAR_RECT.collidepoint(pos):
                    game_state = "NAME_INPUT"
                elif MENU_RANKING_RECT.collidepoint(pos):
                    game_state = "MENU_RANKING"
                elif MENU_TESTES_RECT.collidepoint(pos): 
                    reset_test_board() 
                    game_state = "TEST_MENU"
            
            elif game_state == "TEST_MENU":
                pos = pygame.mouse.get_pos()
                # Se clicar na área do tabuleiro
                if pos[0] < GAME_WIDTH:
                    add_test_balls(5)

            elif game_state == "ASKING" and current_question_index < len(questions):
                pos = pygame.mouse.get_pos()
                
                for i, rect in enumerate(option_rects):
                    if rect.collidepoint(pos):
                        selected_option_index = i
                        current_q = questions[current_question_index]
                        
                        last_answer_correct = (selected_option_index == current_q['correct'])
                        
                        current_question_index += 1
                        game_state = "SELECT_SLOT" 
                        current_slot = BINS // 2 
                        break 

    
    # --- Lógica de Update ---
    if game_state not in ["MAIN_MENU", "MENU_RANKING"]: 
        for ball in balls:
            ball.update()
            
        for score_anim in floating_scores[:]:
            score_anim.update()
            if score_anim.alpha == 0:
                floating_scores.remove(score_anim)

    # --- Lógica de Transição de Estado ---
    all_balls_inactive = all(not ball.active for ball in balls)
    
    if game_state == "DROPPING" and all_balls_inactive and len(balls) > 0:
        balls.clear() 
        
        if current_question_index < len(questions):
            game_state = "ASKING"
        else:
            game_state = "GAME_OVER"
            
            
    if game_state == "GAME_OVER":
        save_ranking(player_name, total_score) 
        game_state = "RANKING"


    
    # --- Desenho ---
    
    if game_state == "MAIN_MENU":
        draw_main_menu()
    
    elif game_state == "MENU_RANKING":
        draw_ranking_screen()
        draw_text("Pressione 'ESC' para voltar ao Menu", STATS_FONT, WHITE, WIDTH // 2, HEIGHT - 70, center=True)
        
    # ### MODIFICADO: Desenho do Modo Teste (Ativo) ###
    elif game_state == "TEST_MENU":
        screen.fill(BG_COLOR) 
        draw_stats_panel()
        draw_board()

        draw_slot_selector()
        
        for ball in balls:
            ball.draw()
            
        # Limpa as bolas inativas enquanto estamos no modo de teste
        balls = [b for b in balls if b.active]
            
        for score_anim in floating_scores:
            score_anim.draw()
        
        draw_text(f"TESTES", SCORE_FONT, WHITE, GAME_WIDTH // 2, 20, center=True)

        #draw_text("Modo de Teste", TITLE_FONT, GOLD, GAME_WIDTH // 2, 80, center=True)
        #draw_text("Use as SETAS para mover", STATS_FONT, WHITE, GAME_WIDTH // 2, 120, center=True)
        #draw_text("[ESPAÇO] = 1 Bola", STATS_FONT, WHITE, GAME_WIDTH // 2, 150, center=True)
        #draw_text("[A] = 3 Bolas", STATS_FONT, WHITE, GAME_WIDTH // 2, 180, center=True)
        #draw_text("[CLIQUE no Tabuleiro] = 5 Bolas", STATS_FONT, WHITE, GAME_WIDTH // 2, 210, center=True)
        draw_text("'R' para Limpar", SMALL_FONT, WHITE, GAME_WIDTH // 2, 80, center=True)
        draw_text("'ESC' para Voltar ao Menu", SMALL_FONT, WHITE, GAME_WIDTH // 2, 95, center=True)

    else:
        # --- Desenha o fundo do jogo (Tabuleiro e Estatísticas) ---
        screen.fill(BG_COLOR) 
        draw_stats_panel()
        draw_board()
        
        for ball in balls:
            ball.draw()
            
        for score_anim in floating_scores:
            score_anim.draw()

        # Desenha a pontuação total (para o jogo normal)
        score_color = GREEN
        if total_score < 0:
            score_color = RED
        elif total_score == 0:
            score_color = WHITE
        
        draw_text(f"PRÊMIO TOTAL: R$ {total_score:,}", SCORE_FONT, score_color, GAME_WIDTH // 2, 20, center=True)
        
        # --- Desenha as sobreposições de estado (em cima do tabuleiro) ---
        if game_state == "NAME_INPUT":
            draw_name_input()
            
        elif game_state == "ASKING":
            draw_text(f"Pergunta {current_question_index + 1} de {len(questions)}", SMALL_FONT, WHITE, GAME_WIDTH // 2, 80, center=True)
            draw_question_panel() 
        
        elif game_state == "SELECT_SLOT":
            draw_slot_selector()
            draw_text("Use as SETAS para mover e ESPAÇO para soltar", SMALL_FONT, WHITE, GAME_WIDTH // 2, 80, center=True)
            
        elif game_state == "DROPPING":
            draw_text(f"Respondendo Pergunta {current_question_index} de {len(questions)}", SMALL_FONT, WHITE, GAME_WIDTH // 2, 80, center=True)
        
        elif game_state == "RANKING":
            # O ranking pós-jogo será um overlay
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(200) 
            overlay.fill(BG_COLOR)
            screen.blit(overlay, (0, 0))
            
            draw_ranking_screen() 
            draw_text("Pressione 'R' para jogar novamente", STATS_FONT, WHITE, WIDTH // 2, HEIGHT - 70, center=True)
            
        if game_state in ["ASKING", "SELECT_SLOT", "DROPPING", "NAME_INPUT"]:
             draw_text("'R' para Resetar", SMALL_FONT, WHITE, GAME_WIDTH // 2, 100, center=True)

    
    pygame.display.flip()
    clock.tick(60) 

pygame.quit()