import pygame
import random
import math
import time

pygame.init()
pygame.font.init()


WIDTH, HEIGHT = 1200, 700  
GAME_WIDTH = 800         
STATS_WIDTH = 400        

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jogo da Distribuição de Probabilidade - Estilo 'The Wall'")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (230, 230, 230)
BLUE = (30, 144, 255)
RED = (255, 69, 0)
GREEN = (40, 190, 40)
GOLD = (255, 215, 0)
BG_COLOR = (20, 20, 40) 
PEG_COLOR = (150, 150, 170)

TITLE_FONT = pygame.font.SysFont('Arial', 30, bold=True)
STATS_FONT = pygame.font.SysFont('Arial', 22)
SMALL_FONT = pygame.font.SysFont('Arial', 16)
VALUE_FONT = pygame.font.SysFont('Arial', 18, bold=True)
SCORE_FONT = pygame.font.SysFont('Impact', 60)
FLOATING_FONT = pygame.font.SysFont('Arial', 24, bold=True)
QUESTION_FONT = pygame.font.SysFont('Arial', 26, bold=True)
OPTION_FONT = pygame.font.SysFont('Arial', 22)


ROWS = 12  
BINS = ROWS + 1 
PEG_RADIUS = 5
BALL_RADIUS = 8
START_Y = 50

BIN_WIDTH = GAME_WIDTH / BINS 
PEG_H_SPACING = BIN_WIDTH 
PEG_V_SPACING = 45 

BIN_VALUES = [
    10000, 5000, 2000, 1000, 500, 10, 1, 10, 500, 1000, 2000, 5000, 10000
]

# --- Variáveis de Jogo ---
bin_counts = [0] * BINS
total_balls = 0
total_score = 0 
balls = [] 
pegs = []  
floating_scores = []
option_rects = [] # Para detectar cliques nas opções

# --- Perguntas ---
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
    }
]
random.shuffle(questions) # Embaralha as perguntas

# --- Estado do Jogo ---
game_state = "ASKING" # "ASKING", "DROPPING", "GAME_OVER"
current_question_index = 0


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
    # Modificado para aceitar 'is_correct'
    def __init__(self, x, y, value, is_correct):
        self.x = x
        self.y = y
        self.value = value
        self.is_correct = is_correct # Salva se foi de uma resposta correta
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
            
            # Define o texto e a cor baseado se foi acerto ou erro
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
    # Modificado para aceitar 'is_correct'
    def __init__(self, is_correct):
        self.x = GAME_WIDTH // 2 + random.randint(-5, 5) 
        self.y = START_Y
        self.vy = 0
        self.vx = 0
        self.current_row = 0 
        self.target_peg_y = pegs[0][0][1] 
        self.active = True
        self.is_correct = is_correct # Salva o status da resposta
        self.color = GREEN if is_correct else RED # Define a cor da bola

    def update(self):
        if not self.active:
            return

        
        self.vy += 0.5
        self.y += self.vy
        self.x += self.vx

        
        if self.current_row < ROWS and self.y >= self.target_peg_y:
            self.y = self.target_peg_y 
            
            self.vx = random.choice([-1, 1]) * 2.5 
            self.vy = -1 
            
            self.current_row += 1  
            
            
            if self.current_row < ROWS:
                self.target_peg_y = pegs[self.current_row][0][1] 
            
        
        elif self.current_row == ROWS and self.y > pegs[-1][0][1] + PEG_V_SPACING:
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
                
                # --- LÓGICA DE PONTUAÇÃO MODIFICADA ---
                if self.is_correct:
                    total_score += value_won
                    floating_scores.append(FloatingScore(self.x, self.y - 20, value_won, is_correct=True))
                else:
                    total_score -= value_won
                    floating_scores.append(FloatingScore(self.x, self.y - 20, value_won, is_correct=False))
                # --- FIM DA LÓGICA MODIFICADA ---


    def draw(self):
        
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), BALL_RADIUS)
        pygame.draw.circle(screen, WHITE, (int(self.x) - 2, int(self.y) - 2), int(BALL_RADIUS // 2.5))


# --- NOVA FUNÇÃO ---
def draw_question_panel():
    global option_rects
    option_rects.clear()
    
    # Cria uma sobreposição escura semi-transparente
    overlay = pygame.Surface((GAME_WIDTH, HEIGHT))
    overlay.set_alpha(200) # Nível de transparência
    overlay.fill(BG_COLOR)
    screen.blit(overlay, (0, 0))
    
    # Desenha a caixa da pergunta
    box_rect = pygame.Rect(GAME_WIDTH // 4 - 50, HEIGHT // 4, GAME_WIDTH // 2 + 100, HEIGHT // 2 + 50)
    pygame.draw.rect(screen, LIGHT_GRAY, box_rect, border_radius=15)
    pygame.draw.rect(screen, BLUE, box_rect, 5, border_radius=15)
    
    if current_question_index < len(questions):
        current_q = questions[current_question_index]
        
        # Desenha o texto da pergunta
        draw_text(current_q["question"], QUESTION_FONT, BLACK, box_rect.centerx, box_rect.y + 40, center=True)
        
        # Desenha as opções
        option_y_start = box_rect.y + 100
        option_height = (box_rect.height - 120) / 4
        
        for i, option in enumerate(current_q["options"]):
            option_text = f"{i+1}. {option}"
            
            # Cria o retângulo clicável para a opção
            option_box = pygame.Rect(box_rect.x + 30, option_y_start + i * option_height, box_rect.width - 60, option_height - 10)
            option_rects.append(option_box) # Salva o retângulo para detecção de clique
            
            # Destaca a opção se o mouse estiver sobre ela (hover)
            pos = pygame.mouse.get_pos()
            if option_box.collidepoint(pos):
                pygame.draw.rect(screen, GRAY, option_box, border_radius=10)
            else:
                pygame.draw.rect(screen, WHITE, option_box, border_radius=10)
                
            pygame.draw.rect(screen, BLACK, option_box, 2, border_radius=10)
            
            # Desenha o texto da opção
            draw_text(option_text, OPTION_FONT, BLACK, option_box.x + 15, option_box.centery, center_y=True)
    else:
        # Se as perguntas acabaram
        draw_text("Fim de Jogo!", TITLE_FONT, BLACK, box_rect.centerx, box_rect.centery - 20, center=True, center_y=True)
        draw_text("Pressione 'R' para reiniciar", STATS_FONT, BLACK, box_rect.centerx, box_rect.centery + 20, center=True, center_y=True)


def setup_board():
    
    pegs.clear()
    for r in range(ROWS):
        row_pegs = []
        num_pegs_in_row = r + 1
        
        row_width = (num_pegs_in_row - 1) * PEG_H_SPACING
        start_x = (GAME_WIDTH - row_width) / 2
        
        peg_y = START_Y + 100 + r * PEG_V_SPACING
        
        for i in range(num_pegs_in_row):
            peg_x = start_x + i * PEG_H_SPACING
            row_pegs.append((int(peg_x), int(peg_y)))
        pegs.append(row_pegs)

def draw_board():
    
    for row in pegs:
        for pos in row:
            pygame.draw.circle(screen, PEG_COLOR, pos, PEG_RADIUS)
            
    bin_base_y = HEIGHT - 80
    
    
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



running = True
setup_board() 

# --- LOOP PRINCIPAL MODIFICADO ---
while running:
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.KEYDOWN:
            # REMOVIDO: Lançar bola com ESPAÇO
            if event.key == pygame.K_r: 
                # Lógica de Reset atualizada
                bin_counts = [0] * BINS
                total_balls = 0
                total_score = 0
                balls.clear()
                floating_scores.clear()
                current_question_index = 0  # Reinicia as perguntas
                game_state = "ASKING"       # Volta ao estado de pergunta
                random.shuffle(questions)   # Embaralha para o próximo jogo
                
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Lógica de clique do mouse completamente modificada
            
            # Só aceita cliques se estivermos no estado "ASKING"
            if game_state == "ASKING" and current_question_index < len(questions):
                pos = pygame.mouse.get_pos()
                
                # Verifica se o clique foi em algum retângulo de opção
                for i, rect in enumerate(option_rects):
                    if rect.collidepoint(pos):
                        # Resposta selecionada
                        selected_option_index = i
                        current_q = questions[current_question_index]
                        
                        # Verifica se a resposta está correta
                        is_correct = (selected_option_index == current_q['correct'])
                        
                        # Lança UMA bola com o status de correta ou incorreta
                        balls.append(Ball(is_correct=is_correct)) 
                        
                        # Avança para a próxima pergunta/estado
                        current_question_index += 1
                        game_state = "DROPPING" # Muda o estado para "bola caindo"
                        break # Para de checar os outros retângulos

    
    # --- Lógica de Update ---
    for ball in balls:
        ball.update()
        
    for score_anim in floating_scores[:]:
        score_anim.update()
        if score_anim.alpha == 0:
            floating_scores.remove(score_anim)

    # --- Lógica de Transição de Estado ---
    # Verifica se todas as bolas pararam de se mover
    all_balls_inactive = all(not ball.active for ball in balls)
    
    if game_state == "DROPPING" and all_balls_inactive and len(balls) > 0:
        balls.clear() # Limpa a bola que terminou de cair
        
        if current_question_index < len(questions):
            # Se ainda há perguntas, volta a perguntar
            game_state = "ASKING"
        else:
            # Se as perguntas acabaram, fim de jogo
            game_state = "GAME_OVER"

    
    # --- Desenho ---
    screen.fill(BG_COLOR) 
    
    draw_stats_panel()
    draw_board()
    
    for ball in balls:
        ball.draw()
        
    for score_anim in floating_scores:
        score_anim.draw()

    # Define a cor da pontuação baseada no valor
    score_color = GREEN
    if total_score < 0:
        score_color = RED
    elif total_score == 0:
        score_color = WHITE
        
    draw_text(f"PRÊMIO TOTAL: R$ {total_score:,}", SCORE_FONT, score_color, GAME_WIDTH // 2, 20, center=True)
    
    # --- Desenha textos de ajuda ou painel de pergunta ---
    if game_state == "ASKING":
        draw_text(f"Pergunta {current_question_index + 1} de {len(questions)}", SMALL_FONT, WHITE, GAME_WIDTH // 2, 80, center=True)
        draw_question_panel() # Desenha a pergunta por cima
    
    elif game_state == "GAME_OVER":
        draw_text("Fim de Jogo! Pressione 'R' para reiniciar.", TITLE_FONT, GOLD, GAME_WIDTH // 2, 80, center=True)
    
    elif game_state == "DROPPING":
        # Mostra a pergunta atual (que foi respondida)
        draw_text(f"Respondendo Pergunta {current_question_index} de {len(questions)}", SMALL_FONT, WHITE, GAME_WIDTH // 2, 80, center=True)

    draw_text("'R' para Resetar", SMALL_FONT, WHITE, GAME_WIDTH // 2, 100, center=True)

    
    pygame.display.flip()
    clock.tick(60) 

pygame.quit()