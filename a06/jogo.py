import pygame
import random
import sys
import os
import time 
from perguntas_banco import PERGUNTAS 

# --- Configurações do Pygame ---
pygame.init()

LARGURA_TELA = 1024
ALTURA_TELA = 768
TELA = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
pygame.display.set_caption("Road Quiz")

# --- Cores ---
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
CINZA = (100, 100, 100)
VERDE = (0, 200, 0)
VERMELHO = (200, 0, 0)
AZUL = (0, 0, 200)
AMARELO = (255, 255, 0) # Para as linhas da pista
CIANO = (0, 255, 255) # Para o texto de vidas
LARANJA = (255, 165, 0) # NOVO: Cor laranja para o fundo da pergunta

# --- Fontes ---
FONTE_PERGUNTA = pygame.font.Font(None, 40)
FONTE_ALTERNATIVA = pygame.font.Font(None, 30)
FONTE_MENSAGEM = pygame.font.Font(None, 60)
FONTE_PONTUACAO = pygame.font.Font(None, 35)
FONTE_NUMEROS_GRANDES = pygame.font.Font(None, 60) # NOVO: Fonte maior para os números


# --- Velocidades ---
VELOCIDADE_PISTA = 5
VELOCIDADE_PORTAO = 5
VELOCIDADE_CARRO = 7 # Esta é a velocidade lateral do carro
VELOCIDADE_TRANSICAO = 10 # Velocidade do carro na transição

# --- Carro Dimensões DESEJADAS (máximas) ---
LARGURA_CARRO = 110 # Aumentado para melhor visualização
ALTURA_CARRO = 110 # Aumentado para melhor visualização

# --- Posição Inicial do Carro ---
POS_INICIAL_CARRO_X = LARGURA_TELA // 2 - LARGURA_CARRO // 2
POS_INICIAL_CARRO_Y = ALTURA_TELA - ALTURA_CARRO - 50

# --- Ajuste de Hitbox (NOVO) ---
# Valores negativos para reduzir a hitbox em relação ao tamanho da imagem/área de desenho.
# Ex: -60 significa reduzir 30px de cada lado (total 60px de largura/altura).
CARRO_HITBOX_WIDTH_REDUCTION = -60 
CARRO_HITBOX_HEIGHT_REDUCTION = -60

OBSTACULO_HITBOX_WIDTH_REDUCTION = -20
OBSTACULO_HITBOX_HEIGHT_REDUCTION = -20


# Variáveis globais para as imagens do carro e da pista
IMAGEM_CARRO_RETO = None
IMAGEM_CARRO_ESQUERDA = None
IMAGEM_CARRO_DIREITA = None
IMAGEM_PISTA_FUNDO = None # Nova variável para a imagem de fundo da pista
IMAGEM_CORACAO = None
IMAGEM_PONTUACAO = None
IMAGEM_GAMEOVER_FUNDO = None # NOVO: Variável global para a imagem de fundo do Game Over


# --- Variáveis Globais para o Jogo de Sequência (NOVO) ---
sequencia_gerada = [] # A sequência de cores/direções a ser lembrada
sequencia_atual_idx = 0 # O índice do elemento atual na sequência que o jogador deve reproduzir
mostrando_sequencia = False # True se o jogo estiver mostrando a sequência ao jogador
tempo_inicio_mostrar_sequencia = 0 # Tempo em que o elemento atual da sequência começou a ser mostrado
tempo_inicio_resposta = 0 # Tempo em que o jogador começou a responder
zona_alvo_atual = None # A zona (LEFT/RIGHT) que está ativa para o jogador pressionar
ELEMENTOS_SEQUENCIA_DISPONIVEIS = ["esquerda", "direita"] # Quais elementos podem aparecer na sequência

# --- Funções de Ajuda para Imagens ---
def escalar_imagem_mantendo_proporcao(imagem, largura_alvo, altura_alvo):
    """
    Escala uma imagem para se encaixar dentro de um tamanho alvo, mantendo sua proporção.
    A imagem resultante pode ser menor que o tamanho alvo em uma das dimensões.
    """
    largura_original, altura_original = imagem.get_size()
    
    # Calcula a razão de aspecto
    razao_aspecto_original = largura_original / altura_original
    razao_aspecto_alvo = largura_alvo / altura_alvo

    if razao_aspecto_original > razao_aspecto_alvo:
        # Imagem original é mais larga que o alvo, escala pela largura
        nova_largura = largura_alvo
        nova_altura = int(nova_largura / razao_aspecto_original)
    else:
        # Imagem original é mais alta ou tem a mesma proporção, escala pela altura
        nova_altura = altura_alvo
        nova_largura = int(nova_altura * razao_aspecto_original)
    
    return pygame.transform.scale(imagem, (nova_largura, nova_altura))


# Nomes dos arquivos de imagem (certifique-se de que correspondem aos seus arquivos na pasta 'imagens')
# Estes são carregamentos iniciais para evitar erros de referência antes da fase ser carregada
try:
    temp_img = pygame.image.load(os.path.join('..', 'imagens', 'img_carrofrente.png'))
    IMAGEM_CARRO_RETO = escalar_imagem_mantendo_proporcao(temp_img, LARGURA_CARRO, ALTURA_CARRO)
except pygame.error:
    print("Aviso: 'img_carrofrente.png' não encontrada. Usando forma padrão.")
    IMAGEM_CARRO_RETO = None 

try:
    temp_img = pygame.image.load(os.path.join('..', 'imagens', 'img_carroesquerda.png'))
    IMAGEM_CARRO_ESQUERDA = escalar_imagem_mantendo_proporcao(temp_img, LARGURA_CARRO, ALTURA_CARRO)
except pygame.error:
    print("Aviso: 'img_carroesquerda.png' não encontrada.")
    IMAGEM_CARRO_ESQUERDA = None

try:
    temp_img = pygame.image.load(os.path.join('..', 'imagens', 'img_carrodireita.png'))
    IMAGEM_CARRO_DIREITA = escalar_imagem_mantendo_proporcao(temp_img, LARGURA_CARRO, ALTURA_CARRO)
except pygame.error:
    print("Aviso: 'img_carrodireita.png' não encontrada.")
    IMAGEM_CARRO_DIREITA = None

try:
    # ATENÇÃO: Verifique o nome do arquivo da sua imagem de coração
    temp_img = pygame.image.load(os.path.join('..', 'imagens', 'img_coracao.png'))
    # Aumentando para 50x50 pixels (ajuste conforme o desejado)
    IMAGEM_CORACAO = pygame.transform.scale(temp_img, (50, 50)) 
except pygame.error:
    print("Aviso: 'img_coracao.png' não encontrada. Vidas serão mostradas como texto.")
    IMAGEM_CORACAO = None 

try:
    # ATENÇÃO: Verifique o nome do arquivo da sua imagem de pontuação (ex: img_estrela.png)
    temp_img_pontuacao = pygame.image.load(os.path.join('..', 'imagens', 'img_estrela.png'))
    # Aumentando para 50x50 pixels (ajuste conforme o desejado)
    IMAGEM_PONTUACAO = pygame.transform.scale(temp_img_pontuacao, (50, 50)) 
except pygame.error:
    print("Aviso: 'img_estrela.png' não encontrada. Pontuação será mostrada como texto.")
    IMAGEM_PONTUACAO = None

try:
    # ATENÇÃO: Verifique o nome do arquivo da sua imagem de fundo de Game Over
    temp_img_gameover_fundo = pygame.image.load(os.path.join('..', 'imagens', 'img_gameover_fundo.png'))
    # Escalar para o tamanho da tela para que cubra todo o fundo
    IMAGEM_GAMEOVER_FUNDO = pygame.transform.scale(temp_img_gameover_fundo, (LARGURA_TELA, ALTURA_TELA)) 
except pygame.error:
    print("Aviso: 'img_gameover_fundo.png' não encontrada. Tela de Game Over usará fundo preto.")
    IMAGEM_GAMEOVER_FUNDO = None # Se a imagem não for encontrada, o fundo continuará preto

# --- Portões ---
LARGURA_PORTAO = 150
ALTURA_PORTAO = 100
ESPACAMENTO_PORTAO_X = 80 
ESPACAMENTO_PORTAO_Y = 200 
try:
    temp_img = pygame.image.load(os.path.join('..', 'imagens', 'img_portao.png'))
    IMAGEM_PORTAO = escalar_imagem_mantendo_proporcao(temp_img, LARGURA_PORTAO, ALTURA_PORTAO)
except pygame.error:
    IMAGEM_PORTAO = None # Se a imagem não for encontrada, desenha um retângulo

# --- Configurações das Fases ---
FASES = [
    {
        "nome": "Fase 1 - Idade Média (Quiz)",
        "tipo": "quiz", 
        "acertos_para_proxima": 0,
        "pista_imagem": "img_pista_medieval.png", 
        "carro_reto_imagem": "img_carrofrente.png",
        "carro_esquerda_imagem": "img_carroesquerda.png",
        "carro_direita_imagem": "img_carrodireita.png"
    },
    {
        "nome": "Fase 2 - Futurista (Quiz)",
        "tipo": "quiz",
        "acertos_para_proxima": 3, 
        "pista_imagem": "img_pista_futurista.png", 
        "carro_reto_imagem": "img_navefrente.png",
        "carro_esquerda_imagem": "img_naveesquerda.png",
        "carro_direita_imagem": "img_navedireita.png"
    },
    {
        "nome": "Fase 3 - Cidade Grande (Quiz)",
        "tipo": "quiz",
        "acertos_para_proxima": 6, 
        "pista_imagem": "img_pista_cidade.png",
        "carro_reto_imagem": "img_carrocidadefrente.png",
        "carro_esquerda_imagem": "img_carrocidadeesquerda.png",
        "carro_direita_imagem": "img_carrocidadedireita.png"
    },
    {
        "nome": "Fase 4 - Desvio de Meteoros (Obstáculos)", 
        "tipo": "obstaculos", 
        "acertos_para_proxima": 8, 
        "duracao_fase_obstaculo": 20000, 
        "intervalo_geracao_obstaculo_min": 240, 
        "intervalo_geracao_obstaculo_max": 480, 
        "pista_imagem": "img_pista_espaco.png", 
        "carro_reto_imagem": "img_navefrente.png", 
        "carro_esquerda_imagem": "img_naveesquerda.png",
        "carro_direita_imagem": "img_navedireita.png",
        "obstaculo_imagem": "img_meteoro.png", 
        "velocidade_obstaculo": 8 
    },
    { 
        "nome": "Fase 5 - Céus (Quiz)",
        "tipo": "quiz",
        "acertos_para_proxima": 8, # ATENÇÃO: Ajustado de 9 para 8, para transicionar imediatamente após fase 4.
        "pista_imagem": "img_pista_ceu.png", # Imagem de pista no céu
        "carro_reto_imagem": "img_aviaofrente.png",
        "carro_esquerda_imagem": "img_aviaoesquerda.png",
        "carro_direita_imagem": "img_aviaodireita.png"
    },
    { 
        "nome": "Fase 6 - Mar (Quiz)",
        "tipo": "quiz",
        "acertos_para_proxima": 10, 
        "pista_imagem": "img_pista_mar.png",
        "carro_reto_imagem": "img_carromarfrente.png",
        "carro_esquerda_imagem": "img_carromaresquerda.png",
        "carro_direita_imagem": "img_carromardireita.png"
    },
    { 
        "nome": "Fase 7 - Oceano (Quiz)",
        "tipo": "quiz",
        "acertos_para_proxima": 12, 
        "pista_imagem": "img_pista_oceano.png", 
        "carro_reto_imagem": "img_submarinofrente.png",
        "carro_esquerda_imagem": "img_submarinoesquerda.png",
        "carro_direita_imagem": "img_submarinodireita.png"
    },
    {
        "nome": "Fase 8 - Desafio da Sequência",
        "tipo": "sequencia", # Novo tipo de fase
        "acertos_para_proxima": 20, # A pontuação *mínima* para passar dessa fase (se ela não der pontos, mantém o último)
        "pista_imagem": "img_pista_sequencia.png", # Nova imagem de pista para a fase de sequência
        "carro_reto_imagem": "img_navefrente.png", # Reutilizando a nave para esta fase
        "carro_esquerda_imagem": "img_naveesquerda.png",
        "carro_direita_imagem": "img_navedireita.png",
        "num_elementos_sequencia_inicial": 3, # Começa com 3 elementos na sequência
        "tempo_mostrar_elemento": 700, # Tempo que cada elemento é mostrado (ms)
        "tempo_espera_entre_elementos": 300, # Tempo de pausa entre mostrar elementos (ms)
        "tempo_para_resposta": 1500 # Tempo para o jogador responder a cada elemento (ms)
    }
]

# --- Variáveis Globais do Jogo (estado atual) ---
carro_x = POS_INICIAL_CARRO_X
carro_y = POS_INICIAL_CARRO_Y
pista_y_offset = 0 # Para simular o movimento da pista

portoes = [] 
obstaculos = [] 

# pergunta_atual_idx = 0 # NÃO USADO DIRETAMENTE PARA SELEÇÃO DE PERGUNTAS AGORA
pergunta_ativa = False
mensagem_exibida = ""
tempo_mensagem = 0

TEMPO_EXIBIR_MENSAGEM = 1500 # milissegundos
pode_escolher = True 
pontuacao = 0

TOTAL_VIDAS = 3 
vidas_restantes = TOTAL_VIDAS 

carro_rotacao_estado = "reto" 
fase_atual_idx = 0 
tempo_inicio_fase_obstaculo = 0 
proximo_obstaculo_tempo = 0 

# --- NOVAS VARIÁVEIS GLOBAIS PARA CONTROLE DE PERGUNTAS ---
perguntas_restantes = [] # Lista de perguntas disponíveis para o quiz atual
pergunta_selecionada_quiz = None # A pergunta que está sendo exibida no momento

# --- Estados do Jogo ---
GAME_STATE_MENU = -1 # Novo estado para o menu inicial
GAME_STATE_HOW_TO_PLAY = -2 # Novo estado para a tela "Como Jogar"
GAME_STATE_PLAYING = 0      
GAME_STATE_SHOW_MESSAGE = 1 
GAME_STATE_TRANSITION = 2   
GAME_STATE_END_GAME = 3     
GAME_STATE_OBSTACLE_COLLISION_PAUSE = 4 

estado_atual_jogo = GAME_STATE_MENU # O jogo começa no menu

colidiu_com_portao_correto = False 
portao_correto_passado = None 

# --- Funções do Jogo ---

def carregar_recursos_fase():
    """Carrega as imagens do carro e da pista para a fase atual."""
    global IMAGEM_CARRO_RETO, IMAGEM_CARRO_ESQUERDA, IMAGEM_CARRO_DIREITA, IMAGEM_PISTA_FUNDO

    fase = FASES[fase_atual_idx]

    # Carrega a imagem do carro reto
    try:
        temp_img = pygame.image.load(os.path.join('..', 'imagens', fase["carro_reto_imagem"]))
        IMAGEM_CARRO_RETO = escalar_imagem_mantendo_proporcao(temp_img, LARGURA_CARRO, ALTURA_CARRO)
    except pygame.error:
        print(f"Aviso: '{fase['carro_reto_imagem']}' não encontrada para a fase {fase['nome']}. Carro reto será um retângulo.")
        IMAGEM_CARRO_RETO = None 

    # Carrega a imagem do carro virado para a esquerda
    try:
        temp_img = pygame.image.load(os.path.join('..', 'imagens', fase["carro_esquerda_imagem"]))
        IMAGEM_CARRO_ESQUERDA = escalar_imagem_mantendo_proporcao(temp_img, LARGURA_CARRO, ALTURA_CARRO)
    except pygame.error:
        print(f"Aviso: '{fase['carro_esquerda_imagem']}' não encontrada para a fase {fase['nome']}. Carro esquerdo será o reto ou retângulo.")
        IMAGEM_CARRO_ESQUERDA = None

    # Carrega a imagem do carro virado para a direita
    try:
        temp_img = pygame.image.load(os.path.join('..', 'imagens', fase["carro_direita_imagem"]))
        IMAGEM_CARRO_DIREITA = escalar_imagem_mantendo_proporcao(temp_img, LARGURA_CARRO, ALTURA_CARRO)
    except pygame.error:
        print(f"Aviso: '{fase['carro_direita_imagem']}' não encontrada para a fase {fase['nome']}. Carro direito será o reto ou retângulo.")
        IMAGEM_CARRO_DIREITA = None

    # Carrega a imagem de fundo da pista
    try:
        temp_img = pygame.image.load(os.path.join('..', 'imagens', fase["pista_imagem"]))
        IMAGEM_PISTA_FUNDO = pygame.transform.scale(temp_img, (LARGURA_TELA, ALTURA_TELA)) 
    except pygame.error:
        print(f"Aviso: '{fase['pista_imagem']}' não encontrada para a fase {fase['nome']}. Usando linhas padrão.")
        IMAGEM_PISTA_FUNDO = None # Se não encontrar, desenhar_pista usará as linhas

def desenhar_pista():
    global pista_y_offset
    
    # Se houver uma imagem de fundo para a pista, desenhe-a
    if IMAGEM_PISTA_FUNDO:
        # Desenha a imagem da pista duas vezes para criar um efeito de rolagem contínua
        TELA.blit(IMAGEM_PISTA_FUNDO, (0, pista_y_offset - ALTURA_TELA))
        TELA.blit(IMAGEM_PISTA_FUNDO, (0, pista_y_offset))
        
        pista_y_offset += VELOCIDADE_PISTA
        if pista_y_offset >= ALTURA_TELA:
            pista_y_offset = 0
    else:
        # Código padrão de desenho de linhas da pista se não houver imagem
        pygame.draw.rect(TELA, CINZA, (LARGURA_TELA // 4, 0, LARGURA_TELA // 2, ALTURA_TELA)) # Pista central
        num_linhas = 10
        altura_linha = 30
        espaco_entre_linhas = 50
        for i in range(num_linhas):
            y = (i * (altura_linha + espaco_entre_linhas) + pista_y_offset) % (ALTURA_TELA + espaco_entre_linhas)
            pygame.draw.rect(TELA, AMARELO, (LARGURA_TELA // 2 - 5, y, 10, altura_linha)) # Linhas amarelas para destacar
        pista_y_offset += VELOCIDADE_PISTA
        if pista_y_offset >= ALTURA_TELA:
            pista_y_offset = 0

def desenhar_carro(x, y):
    global carro_rotacao_estado # Precisamos ler o estado de rotação do carro
    
    imagem_atual_carro = None
    if carro_rotacao_estado == "esquerda" and IMAGEM_CARRO_ESQUERDA:
        imagem_atual_carro = IMAGEM_CARRO_ESQUERDA
    elif carro_rotacao_estado == "direita" and IMAGEM_CARRO_DIREITA:
        imagem_atual_carro = IMAGEM_CARRO_DIREITA
    elif IMAGEM_CARRO_RETO: # Padrão, mesmo que as outras não existam
        imagem_atual_carro = IMAGEM_CARRO_RETO
    
    if imagem_atual_carro:
        # Centraliza a imagem do carro dentro do espaço LARGURA_CARRO x ALTURA_CARRO
        # Isso é importante porque a imagem pode ser menor devido à preservação da proporção
        img_rect = imagem_atual_carro.get_rect(center=(x + LARGURA_CARRO // 2, y + ALTURA_CARRO // 2))
        TELA.blit(imagem_atual_carro, img_rect.topleft)
    else:
        # Se nenhuma imagem rotacionada foi carregada, desenha um retângulo azul
        pygame.draw.rect(TELA, AZUL, (x, y, LARGURA_CARRO, ALTURA_CARRO))

def iniciar_nova_rodada(): # Renomeada de criar_portoes()
    global pergunta_ativa, portoes, pode_escolher, estado_atual_jogo, vidas_restantes, carro_rotacao_estado
    global obstaculos, tempo_inicio_fase_obstaculo, proximo_obstaculo_tempo 
    global sequencia_gerada, sequencia_atual_idx, mostrando_sequencia, tempo_inicio_mostrar_sequencia, tempo_inicio_resposta, zona_alvo_atual 
    global ELEMENTOS_SEQUENCIA_DISPONIVEIS 
    global perguntas_restantes # NOVO: Variável global para as perguntas restantes
    global pergunta_selecionada_quiz # NOVO: A pergunta que está ativa na rodada

    fase = FASES[fase_atual_idx]

    # PRIORIDADE: Lógica de Fim de Jogo (vidas zeradas)
    if vidas_restantes <= 0:
        estado_atual_jogo = GAME_STATE_END_GAME
        return
    
    # --- NOVO: Lógica para esgotar perguntas em fases de quiz ---
    # Se for uma fase de quiz e não houver mais perguntas disponíveis
    if fase["tipo"] == "quiz" and not perguntas_restantes:
        print("Todas as perguntas foram utilizadas! Jogo encerrado ou um novo ciclo de perguntas será iniciado.")
        estado_atual_jogo = GAME_STATE_END_GAME 
        return

    # Limpa elementos da fase anterior
    portoes = []
    obstaculos = []
    carro_rotacao_estado = "reto" # Resetar rotação do carro para a nova rodada/fase

    if fase["tipo"] == "quiz":
        pergunta_ativa = True
        pode_escolher = True
        
        # Certifica-se de que há perguntas antes de tentar selecionar uma
        if not perguntas_restantes:
            print("AVISO: Sem perguntas disponíveis para quiz. Recarregando todas.")
            # Se todas as perguntas foram usadas, recarregue para um novo ciclo (opcional)
            perguntas_restantes = list(PERGUNTAS) 
            random.shuffle(perguntas_restantes)

        # --- MUDANÇA AQUI: Selecionar e remover a pergunta da lista de disponíveis ---
        pergunta_selecionada_quiz = random.choice(perguntas_restantes) # Seleciona uma pergunta aleatória
        perguntas_restantes.remove(pergunta_selecionada_quiz) # Remove a pergunta para não ser repetida
        
        # Validação: Garante que a pergunta está bem formatada
        if "alternativas" not in pergunta_selecionada_quiz or not isinstance(pergunta_selecionada_quiz["alternativas"], list) or len(pergunta_selecionada_quiz["alternativas"]) < 2:
            print(f"Erro: Uma pergunta selecionada está malformada: {pergunta_selecionada_quiz.get('pergunta', 'Pergunta Desconhecida')}. Encerrando jogo.")
            estado_atual_jogo = GAME_STATE_END_GAME
            return

        alternativas_shuffled = list(pergunta_selecionada_quiz["alternativas"]) # Usa a pergunta selecionada
        random.shuffle(alternativas_shuffled)

        x_portao_esq = LARGURA_TELA // 2 - LARGURA_PORTAO - ESPACAMENTO_PORTAO_X
        x_portao_dir = LARGURA_TELA // 2 + ESPACAMENTO_PORTAO_X
        y_portao = -ALTURA_PORTAO

        portoes.append({"rect": pygame.Rect(x_portao_esq, y_portao, LARGURA_PORTAO, ALTURA_PORTAO), 
                        "texto": alternativas_shuffled[0]["texto"], 
                        "correta": alternativas_shuffled[0]["correta"]})
        portoes.append({"rect": pygame.Rect(x_portao_dir, y_portao, LARGURA_PORTAO, ALTURA_PORTAO), 
                        "texto": alternativas_shuffled[1]["texto"], 
                        "correta": alternativas_shuffled[1]["correta"]})
        
    elif fase["tipo"] == "obstaculos":
        pergunta_ativa = False
        pode_escolher = False
        tempo_inicio_fase_obstaculo = pygame.time.get_ticks()
        proximo_obstaculo_tempo = pygame.time.get_ticks() + random.randint(fase["intervalo_geracao_obstaculo_min"], fase["intervalo_geracao_obstaculo_max"])
        
    elif fase["tipo"] == "sequencia": # NOVO: Lógica para fase de sequência
        pergunta_ativa = False
        pode_escolher = False # O jogador não escolhe portões, ele responde com as setas
        obstaculos = [] # Garante que não há obstáculos de outras fases
        portoes = [] # Garante que não há portões
        
        # Gera a sequência de "esquerda" ou "direita"
        sequencia_gerada = [random.choice(ELEMENTOS_SEQUENCIA_DISPONIVEIS) for _ in range(fase["num_elementos_sequencia_inicial"])]
        sequencia_atual_idx = 0
        mostrando_sequencia = True # Começa mostrando a sequência
        tempo_inicio_mostrar_sequencia = pygame.time.get_ticks() # Registra o tempo para controlar a exibição
        tempo_inicio_resposta = 0 # Reinicia o tempo de resposta
        zona_alvo_atual = None # Não há zona alvo até o jogador começar a responder
        
    estado_atual_jogo = GAME_STATE_PLAYING # Define o estado como PLAYING no final da configuração da rodada

def desenhar_portoes():
    for portao in portoes:
        if IMAGEM_PORTAO:
            # Posição original do portão para o retângulo de colisão
            portao_rect_colisao = portao["rect"]
            
            # Ajusta a posição Y da imagem do portão para ficar acima do texto
            # A imagem será desenhada no topo do rect de colisão, deslocada para cima
            # Ajuste o valor -30 (ou outro número negativo) para mover mais ou menos para cima
            img_portao_y = portao_rect_colisao.top - 60 # Move a imagem 30 pixels para cima
            
            # Centraliza a imagem do portão na largura e usa a nova altura ajustada
            img_rect = IMAGEM_PORTAO.get_rect(center=(portao_rect_colisao.centerx, img_portao_y + IMAGEM_PORTAO.get_height() // 2))
            TELA.blit(IMAGEM_PORTAO, img_rect.topleft) # Desenha a IMAGEM do portão
        else:
            # Desenha um retângulo verde para o portão se não houver imagem
            pygame.draw.rect(TELA, VERDE, portao["rect"])
        
        # Renderiza o texto da alternativa no centro do portão
        # O texto permanece centralizado no retângulo de colisão original do portão
        texto_superficie = FONTE_ALTERNATIVA.render(portao["texto"], True, BRANCO) # Cor do texto preto para melhor contraste
        texto_ret = texto_superficie.get_rect(center=portao["rect"].center)
        TELA.blit(texto_superficie, texto_ret) # Desenha o TEXTO

def desenhar_obstaculos():
    for obstaculo in obstaculos:
        # Desenha o obstáculo (pode ser um retângulo ou imagem)
        if obstaculo["imagem"]:
            img_rect = obstaculo["imagem"].get_rect(center=obstaculo["rect"].center)
            TELA.blit(obstaculo["imagem"], img_rect.topleft)
        else:
            pygame.draw.rect(TELA, VERMELHO, obstaculo["rect"]) # Cor para o obstáculo

def gerar_obstaculo():
    fase = FASES[fase_atual_idx]
    # Dimensões do obstáculo (pode variar, vamos usar algo genérico)
    largura_obstaculo = random.randint(50, 100)
    altura_obstaculo = random.randint(50, 100)
    
    # Posições possíveis para o obstáculo na pista (entre as bordas da pista)
    min_x = LARGURA_TELA // 4
    max_x = LARGURA_TELA * 3 // 4 - largura_obstaculo

    x = random.randint(min_x, max_x)
    y = -altura_obstaculo # Começa fora da tela

    obstaculo_img = None
    if fase["obstaculo_imagem"]:
        try:
            temp_img = pygame.image.load(os.path.join('..', 'imagens', fase["obstaculo_imagem"]))
            obstaculo_img = escalar_imagem_mantendo_proporcao(temp_img, largura_obstaculo, altura_obstaculo)
        except pygame.error:
            print(f"Aviso: Imagem de obstáculo '{fase['obstaculo_imagem']}' não encontrada.")
            obstaculo_img = None

    # NOVO: Inflar (reduzir) o retângulo da hitbox do obstáculo
    obstacle_rect = pygame.Rect(x, y, largura_obstaculo, altura_obstaculo)
    obstacle_rect = obstacle_rect.inflate(OBSTACULO_HITBOX_WIDTH_REDUCTION, OBSTACULO_HITBOX_HEIGHT_REDUCTION)
    obstaculos.append({"rect": obstacle_rect, "imagem": obstaculo_img})


def mover_elementos_fase(): # Renomeado de mover_portoes()
    # TODAS as variáveis globais que serão MODIFICADAS dentro desta função DEVEM SER DECLARADAS AQUI.
    global pergunta_ativa
    global pode_escolher
    # global pergunta_atual_idx # Não precisa mais aqui
    global mensagem_exibida
    global tempo_mensagem
    global pontuacao
    global estado_atual_jogo
    global colidiu_com_portao_correto
    global portao_correto_passado
    global carro_y 
    global carro_x 
    global pista_y_offset
    global vidas_restantes 
    global fase_atual_idx 
    global obstaculos 
    global tempo_inicio_fase_obstaculo
    global proximo_obstaculo_tempo

    fase = FASES[fase_atual_idx]

    if estado_atual_jogo == GAME_STATE_PLAYING:
        if fase["tipo"] == "quiz":
            # Lógica para mover portões e verificar colisão com portões
            for portao in portoes:
                portao["rect"].y += VELOCIDADE_PORTAO

            if pode_escolher:
                # NOVO: Inflar (reduzir) o retângulo da hitbox do carro
                carro_rect = pygame.Rect(carro_x, carro_y, LARGURA_CARRO, ALTURA_CARRO)
                carro_rect = carro_rect.inflate(CARRO_HITBOX_WIDTH_REDUCTION, CARRO_HITBOX_HEIGHT_REDUCTION)

                for portao in portoes:
                    if carro_rect.colliderect(portao["rect"]):
                        if portao["correta"]:
                            mensagem_exibida = "Correto!"
                            pontuacao += 1
                            estado_atual_jogo = GAME_STATE_TRANSITION
                            colidiu_com_portao_correto = True
                            portao_correto_passado = portao
                        else:
                            mensagem_exibida = "Errado!"
                            vidas_restantes -= 1
                            estado_atual_jogo = GAME_STATE_SHOW_MESSAGE
                            pergunta_ativa = False
                        
                        tempo_mensagem = pygame.time.get_ticks()
                        pode_escolher = False
                        return 
            
            if portoes and portoes[0]["rect"].top > ALTURA_TELA:
                if pergunta_ativa:
                    mensagem_exibida = "Tempo Esgotado!"
                    vidas_restantes -= 1
                    estado_atual_jogo = GAME_STATE_SHOW_MESSAGE
                    tempo_mensagem = pygame.time.get_ticks()
                    pergunta_ativa = False
                    pode_escolher = False

        elif fase["tipo"] == "obstaculos":
            # Lógica para fase de obstáculos
            agora = pygame.time.get_ticks()

            # Gerar obstáculos periodicamente
            if agora >= proximo_obstaculo_tempo:
                gerar_obstaculo() # Chamar generar_obstaculo para criar um novo obstáculo
                proximo_obstaculo_tempo = agora + random.randint(fase["intervalo_geracao_obstaculo_min"], fase["intervalo_geracao_obstaculo_max"])

            # Mover obstáculos e verificar colisão
            for obstaculo in list(obstaculos): # Usar list() para permitir remoção durante iteração
                obstaculo["rect"].y += fase["velocidade_obstaculo"] # Usa velocidade da fase
                
                # NOVO: A hitbox do obstáculo já foi inflada na geração, então a usamos diretamente aqui
                carro_rect = pygame.Rect(carro_x, carro_y, LARGURA_CARRO, ALTURA_CARRO)
                carro_rect = carro_rect.inflate(CARRO_HITBOX_WIDTH_REDUCTION, CARRO_HITBOX_HEIGHT_REDUCTION) # Inflar o carro aqui também

                if carro_rect.colliderect(obstaculo["rect"]): # Agora verifica a colisão das hitboxes ajustadas
                    mensagem_exibida = "Colisão!"
                    vidas_restantes -= 1
                    estado_atual_jogo = GAME_STATE_OBSTACLE_COLLISION_PAUSE # NOVO ESTADO
                    tempo_mensagem = pygame.time.get_ticks()
                    return # Para evitar múltiplas colisões ou processamento extra

                if obstaculo["rect"].top > ALTURA_TELA:
                    obstaculos.remove(obstaculo) # Remove obstáculos que saíram da tela

            # Verificar duração da fase de obstáculos
            if agora - tempo_inicio_fase_obstaculo > fase["duracao_fase_obstaculo"]:
                mensagem_exibida = "Fase de Obstáculos Concluída!"
                tempo_mensagem = pygame.time.get_ticks()
                
                # NOVO: Se a fase de obstáculos for a Fase 4, adiciona 3 vidas
                if fase_atual_idx == 3: # Índice da Fase 4
                    vidas_restantes += 3
                    mensagem_exibida += " Bônus: +3 Vidas!" # Adiciona ao texto existente
                    print(f"BÔNUS! Ganhou 3 vidas ao completar a {fase['nome']}!")
                estado_atual_jogo = GAME_STATE_SHOW_MESSAGE # Exibe mensagem de sucesso e avança
                return

    elif estado_atual_jogo == GAME_STATE_TRANSITION: # Após acerto de pergunta
        # Lógica de transição para o carro passar reto
        if carro_y > -ALTURA_CARRO:
            carro_y -= VELOCIDADE_TRANSICAO
            pista_y_offset += VELOCIDADE_TRANSICAO * 1.5
            if portao_correto_passado:
                portao_correto_passado["rect"].y += VELOCIDADE_TRANSICAO * 1.5
            for p in portoes:
                if p != portao_correto_passado:
                    p["rect"].y += VELOCIDADE_TRANSICAO * 1.5 
        else: # Carro saiu da tela por cima
            carro_y = POS_INICIAL_CARRO_X # Reinicia a posição Y do carro para a parte inferior
            carro_x = POS_INICIAL_CARRO_Y # Reinicia a posição X do carro para o centro
            colidiu_com_portao_correto = False
            portao_correto_passado = None
            
            # Lógica de avanço de fase após transição de pergunta
            proxima_fase_existente = (fase_atual_idx + 1) < len(FASES)
            if vidas_restantes <= 0:
                estado_atual_jogo = GAME_STATE_END_GAME
            elif proxima_fase_existente and pontuacao >= FASES[fase_atual_idx + 1]["acertos_para_proxima"]:
                fase_atual_idx += 1 
                carregar_recursos_fase() 
                print(f"Parabéns! Avançando para: {FASES[fase_atual_idx]['nome']}")
                iniciar_nova_rodada() # Inicia a próxima fase (que pode ser de obstáculos)
                estado_atual_jogo = GAME_STATE_PLAYING # Volta ao estado de jogo normal
            else: # Se não há próxima fase ou acertos suficientes, apenas avança para a próxima pergunta (se houver)
                # Não incrementamos pergunta_atual_idx aqui, pois a seleção é feita por random.choice
                iniciar_nova_rodada() # Cria a próxima pergunta
                estado_atual_jogo = GAME_STATE_PLAYING

    elif estado_atual_jogo == GAME_STATE_OBSTACLE_COLLISION_PAUSE: # NOVO ESTADO: Pausa após colisão com obstáculo
        # Pausa por um tempo após colisão de obstáculo
        if pygame.time.get_ticks() - tempo_mensagem > TEMPO_EXIBIR_MENSAGEM:
            mensagem_exibida = ""
            if vidas_restantes <= 0:
                estado_atual_jogo = GAME_STATE_END_GAME # Vai para tela de fim de jogo se as vidas acabaram
            else:
                # Reinicia a fase de obstáculos do zero, sem perder vida extra (já perdeu uma na colisão)
                carro_x = POS_INICIAL_CARRO_X # Reposiciona o carro
                carro_y = POS_INICIAL_CARRO_Y
                iniciar_nova_rodada() # Recria os obstáculos e zera o tempo da fase
                estado_atual_jogo = GAME_STATE_PLAYING


def desenhar_pergunta():
    global fase_atual_idx 
    global pergunta_ativa 
    global portoes 
    global estado_atual_jogo 
    global pergunta_selecionada_quiz # NOVO: Acessa a pergunta que foi selecionada para esta rodada

    # Desenha a pergunta no topo da tela, apenas se estiver no estado de jogo, a fase for de quiz e houver uma pergunta selecionada
    if FASES[fase_atual_idx]["tipo"] == "quiz" and pergunta_ativa and portoes and pergunta_selecionada_quiz:
        pergunta_texto = pergunta_selecionada_quiz["pergunta"] # Usa a pergunta armazenada globalmente
        texto_superficie = FONTE_PERGUNTA.render(pergunta_texto, True, PRETO) 
        texto_ret = texto_superficie.get_rect(center=(LARGURA_TELA // 2, 50))
        
        # Defina LARANJA no início do seu código junto com as outras cores (se ainda não o fez)
        # LARANJA = (255, 165, 0) # Já está definida no topo

        # 1. Desenha um retângulo LARANJA por trás do texto da pergunta
        # Cria um retângulo um pouco maior que o texto para servir de fundo
        fundo_rect = texto_ret.inflate(20, 10) # Adiciona 20px de largura e 10px de altura ao redor do texto
        pygame.draw.rect(TELA, LARANJA, fundo_rect) # Desenha o retângulo laranja PRIMEIRO
        
        # 2. Desenha o texto por cima do retângulo
        TELA.blit(texto_superficie, texto_ret) 

    # Opcional: Mostrar o nome da fase ou uma mensagem genérica na fase de obstáculos
    elif FASES[fase_atual_idx]["tipo"] == "obstaculos" and estado_atual_jogo == GAME_STATE_PLAYING:
        texto_fase = FONTE_PERGUNTA.render(FASES[fase_atual_idx]["nome"], True, BRANCO)
        texto_ret = texto_fase.get_rect(center=(LARGURA_TELA // 2, 50))
        TELA.blit(texto_fase, texto_ret)
    elif FASES[fase_atual_idx]["tipo"] == "sequencia" and estado_atual_jogo == GAME_STATE_PLAYING: 
        texto_fase = FONTE_PERGUNTA.render(FASES[fase_atual_idx]["nome"], True, BRANCO)
        texto_ret = texto_fase.get_rect(center=(LARGURA_TELA // 2, 50))
        TELA.blit(texto_fase, texto_ret)
        
        if mostrando_sequencia:
            instrucao_texto = FONTE_ALTERNATIVA.render("MEMORIZE A SEQUÊNCIA!", True, AMARELO)
        else:
            instrucao_texto = FONTE_ALTERNATIVA.render("PASSE PELA ZONA CORRETA!", True, AMARELO)
        instrucao_ret = instrucao_texto.get_rect(center=(LARGURA_TELA // 2, 80))
        TELA.blit(instrucao_texto, instrucao_ret)

def exibir_mensagem():
    # TODAS as variáveis globais que serão MODIFICADAS dentro desta função DEVEM SER DECLARADAS AQUI.
    global mensagem_exibida
    global tempo_mensagem
    # global pergunta_atual_idx # Não precisa mais aqui
    global estado_atual_jogo
    global vidas_restantes
    global carro_x 
    global carro_y 
    global fase_atual_idx
    global sequencia_gerada, sequencia_atual_idx, mostrando_sequencia, tempo_inicio_mostrar_sequencia, zona_alvo_atual 

    # Esta função agora é chamada para GAME_STATE_SHOW_MESSAGE e GAME_STATE_OBSTACLE_COLLISION_PAUSE
    if (estado_atual_jogo == GAME_STATE_SHOW_MESSAGE or estado_atual_jogo == GAME_STATE_OBSTACLE_COLLISION_PAUSE) and mensagem_exibida:
        texto_superficie = FONTE_MENSAGEM.render(mensagem_exibida, True, BRANCO)
        texto_ret = texto_superficie.get_rect(center=(LARGURA_TELA // 2, ALTURA_TELA // 2))
        TELA.blit(texto_superficie, texto_ret)

        # Espera um tempo antes de ir para a próxima rodada/fase ou fim de jogo
        if pygame.time.get_ticks() - tempo_mensagem > TEMPO_EXIBIR_MENSAGEM:
            mensagem_exibida = ""
            
            # Se a mensagem foi de colisão na fase de obstáculos, a lógica de avanço é diferente (reiniciar a fase)
            if estado_atual_jogo == GAME_STATE_OBSTACLE_COLLISION_PAUSE:
                if vidas_restantes <= 0:
                    estado_atual_jogo = GAME_STATE_END_GAME
                else:
                    carro_x = POS_INICIAL_CARRO_X
                    carro_y = POS_INICIAL_CARRO_Y
                    iniciar_nova_rodada() 
                    estado_atual_jogo = GAME_STATE_PLAYING
            else: # Era GAME_STATE_SHOW_MESSAGE (feedback de quiz ou fase de obstáculo concluída)
                if vidas_restantes <= 0:
                    estado_atual_jogo = GAME_STATE_END_GAME
                else:
                    # Lógica para avanço de fase APÓS a mensagem (se a mensagem foi de conclusão de fase de obstáculo)
                    proxima_fase_existente = (fase_atual_idx + 1) < len(FASES)
                    if proxima_fase_existente and pontuacao >= FASES[fase_atual_idx + 1]["acertos_para_proxima"]:
                        fase_atual_idx += 1 
                        carregar_recursos_fase() 
                        print(f"Parabéns! Avançando para: {FASES[fase_atual_idx]['nome']}")
                    
                    # Não precisamos mais de pergunta_atual_idx aqui, pois a seleção é dinâmica
                    iniciar_nova_rodada() 
                    estado_atual_jogo = GAME_STATE_PLAYING


def desenhar_pontuacao():
    global vidas_restantes 
    global pontuacao 

    # --- Configuração do SCORE (canto superior direito) ---
    if IMAGEM_PONTUACAO:
        # Posição para o ícone do score
        # LARGURA_TELA - largura_imagem - margem_da_borda
        x_pos_score_icon = LARGURA_TELA - IMAGEM_PONTUACAO.get_width() - 10 
        TELA.blit(IMAGEM_PONTUACAO, (x_pos_score_icon, 10)) 
        
        # Posição para o número do score (ao lado do ícone, alinhado à direita)
        texto_pontuacao_num = FONTE_NUMEROS_GRANDES.render(f"{pontuacao}", True, BRANCO) 
        # Alinha o texto à esquerda do ícone, com um pequeno espaçamento
        x_pos_score_text = x_pos_score_icon - texto_pontuacao_num.get_width() - 5 
        TELA.blit(texto_pontuacao_num, (x_pos_score_text, 10)) 
    else:
        # Fallback se não houver imagem de pontuação
        texto_pontuacao = FONTE_PONTUACAO.render(f"Pontuação: {pontuacao}", True, BRANCO)
        texto_pontuacao_rect = texto_pontuacao.get_rect(topright=(LARGURA_TELA - 10, 10)) # Alinha ao canto superior direito
        TELA.blit(texto_pontuacao, texto_pontuacao_rect)

    # --- Configuração da VIDA (canto inferior direito) ---
    if IMAGEM_CORACAO:
        # Posição para o ícone do coração
        # LARGURA_TELA - largura_imagem - margem_da_borda
        x_pos_vidas_icon = LARGURA_TELA - IMAGEM_CORACAO.get_width() - 10 
        # ALTURA_TELA - altura_imagem - margem_da_borda
        y_pos_vidas_icon = ALTURA_TELA - IMAGEM_CORACAO.get_height() - 10 
        TELA.blit(IMAGEM_CORACAO, (x_pos_vidas_icon, y_pos_vidas_icon)) 
        
        # Posição para o número de vidas (ao lado do ícone, alinhado à direita)
        texto_vidas_num = FONTE_NUMEROS_GRANDES.render(f"{vidas_restantes}", True, BRANCO) 
        # Alinha o texto à esquerda do ícone, com um pequeno espaçamento e alinhado ao topo do ícone
        x_pos_vidas_text = x_pos_vidas_icon - texto_vidas_num.get_width() - 5 
        TELA.blit(texto_vidas_num, (x_pos_vidas_text, y_pos_vidas_icon)) 
    else:
        # Fallback se não houver imagem de coração
        texto_vidas = FONTE_PONTUACAO.render(f"Vidas: {vidas_restantes}", True, CIANO) 
        texto_vidas_rect = texto_vidas.get_rect(bottomright=(LARGURA_TELA - 10, ALTURA_TELA - 10)) # Alinha ao canto inferior direito
        TELA.blit(texto_vidas, texto_vidas_rect)

def tela_fim_de_jogo():
    global estado_atual_jogo, pontuacao, carro_x, carro_y, vidas_restantes
    global carro_rotacao_estado, fase_atual_idx 
    global perguntas_restantes # NOVO: Para resetar ao reiniciar o jogo

    # NOVO: Desenha a imagem de fundo da tela de Game Over
    if IMAGEM_GAMEOVER_FUNDO:
        TELA.blit(IMAGEM_GAMEOVER_FUNDO, (0, 0)) # Desenha a imagem na posição (0,0) para cobrir a tela
    else:
        TELA.fill(PRETO) # Se a imagem não for encontrada, usa o fundo preto padrão
    
    # Texto "GAME OVER!"
    texto_game_over = FONTE_MENSAGEM.render("GAME OVER!", True, VERMELHO) 
    rect_game_over = texto_game_over.get_rect(center=(LARGURA_TELA // 2, ALTURA_TELA // 2 - 120))
    TELA.blit(texto_game_over, rect_game_over)

    # --- Exibição do Score Final com Ícone de Estrela ---
    if IMAGEM_PONTUACAO:
        x_pos_score_icon = LARGURA_TELA // 2 - (IMAGEM_PONTUACAO.get_width() + FONTE_MENSAGEM.size(str(pontuacao))[0] + 10) // 2
        TELA.blit(IMAGEM_PONTUACAO, (x_pos_score_icon, ALTURA_TELA // 2 - 40)) 
        
        texto_pontuacao_final_num = FONTE_MENSAGEM.render(f"{pontuacao}", True, BRANCO) 
        x_pos_score_text = x_pos_score_icon + IMAGEM_PONTUACAO.get_width() + 5 
        TELA.blit(texto_pontuacao_final_num, (x_pos_score_text, ALTURA_TELA // 2 - 40)) 
    else:
        texto_pontuacao_final = FONTE_MENSAGEM.render(f"Pontuação Final: {pontuacao}", True, BRANCO)
        rect_pontuacao_final = texto_pontuacao_final.get_rect(center=(LARGURA_TELA // 2, ALTURA_TELA // 2 - 40))
        TELA.blit(texto_pontuacao_final, rect_pontuacao_final)

    # Mensagem para Reiniciar/Sair
    texto_reiniciar_sair = FONTE_ALTERNATIVA.render("Pressione R para Reiniciar ou ESC para Sair", True, BRANCO) 
    rect_reiniciar_sair = texto_reiniciar_sair.get_rect(center=(LARGURA_TELA // 2, ALTURA_TELA // 2 + 80))
    TELA.blit(texto_reiniciar_sair, rect_reiniciar_sair)

    pygame.display.flip() # Atualiza a tela para exibir as mensagens

    # Loop de eventos exclusivo para a tela de fim de jogo
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False 
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                pontuacao = 0           
                # pergunta_atual_idx = 0  # Não é mais usado diretamente
                carro_x = POS_INICIAL_CARRO_X 
                carro_y = POS_INICIAL_CARRO_Y 
                vidas_restantes = TOTAL_VIDAS 
                carro_rotacao_estado = "reto" 
                fase_atual_idx = 0             
                estado_atual_jogo = GAME_STATE_MENU # Volta para o menu
                # Recarrega as perguntas para um novo jogo
                perguntas_restantes = list(PERGUNTAS) 
                random.shuffle(perguntas_restantes)
                return True 
            elif event.key == pygame.K_ESCAPE: 
                return False 
    return True

def tela_menu_inicial():
    global estado_atual_jogo

    try:
        fundo_menu_img = pygame.image.load(os.path.join('..', 'imagens', 'img_menu_fundo.png'))
        fundo_menu_img = pygame.transform.scale(fundo_menu_img, (LARGURA_TELA, ALTURA_TELA))
    except pygame.error:
        print("Aviso: 'img_menu_fundo.png' não encontrada. Usando fundo preto para o menu.")
        fundo_menu_img = None

    titulo_texto = FONTE_MENSAGEM.render("", True, BRANCO) # Adicionei o título ao menu
    titulo_rect = titulo_texto.get_rect(center=(LARGURA_TELA // 2, ALTURA_TELA // 4))

    largura_botao = 200
    altura_botao = 60
    
    botao_start_rect = pygame.Rect(LARGURA_TELA // 2 - largura_botao // 2, ALTURA_TELA // 2, largura_botao, altura_botao)
    texto_start = FONTE_ALTERNATIVA.render("Iniciar Jogo", True, PRETO)
    texto_start_rect = texto_start.get_rect(center=botao_start_rect.center)

    botao_how_to_play_rect = pygame.Rect(LARGURA_TELA // 2 - largura_botao // 2, ALTURA_TELA // 2 + altura_botao + 20, largura_botao, altura_botao)
    texto_how_to_play = FONTE_ALTERNATIVA.render("Como Jogar", True, PRETO)
    texto_how_to_play_rect = texto_how_to_play.get_rect(center=botao_how_to_play_rect.center)

    TELA.fill(PRETO)
    if fundo_menu_img:
        TELA.blit(fundo_menu_img, (0, 0))

    TELA.blit(titulo_texto, titulo_rect)

    pygame.draw.rect(TELA, VERDE, botao_start_rect)
    TELA.blit(texto_start, texto_start_rect)

    pygame.draw.rect(TELA, AZUL, botao_how_to_play_rect)
    TELA.blit(texto_how_to_play, texto_how_to_play_rect)

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False 
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if botao_start_rect.collidepoint(event.pos):
                    print("Clicou em Iniciar Jogo!")
                    estado_atual_jogo = GAME_STATE_PLAYING 
                    return True 
                elif botao_how_to_play_rect.collidepoint(event.pos):
                    print("Clicou em Como Jogar!")
                    estado_atual_jogo = GAME_STATE_HOW_TO_PLAY # Altera para o novo estado
                    return True
    return True 

def tela_como_jogar():
    global estado_atual_jogo

    # Fundo simples para a tela de instruções
    TELA.fill(PRETO)

    # Título da tela
    titulo_instrucoes = FONTE_MENSAGEM.render("Como Jogar", True, BRANCO)
    titulo_rect = titulo_instrucoes.get_rect(center=(LARGURA_TELA // 2, ALTURA_TELA // 8))
    TELA.blit(titulo_instrucoes, titulo_rect)

    # Texto das instruções (adaptar conforme a necessidade)
    instrucoes = [
        "Bem-vindo ao Road Quiz!",
        "Dirija seu veículo para as portas com a resposta correta.",
        "Setas ESQUERDA e DIREITA para mover o veículo.",
        "Acerte perguntas para avançar nas fases e mudar de cenário/veículo.",
        "Em fases de desvio de obstáculos, desvie para não perder vidas!",
        "Ganhe vidas extras ao completar desafios de desvio.",
        "Se suas vidas chegarem a zero, é fim de jogo!",
        "", # Linha em branco para espaçamento
        "Pressione ESC para Voltar ao Menu"
    ]

    y_pos = ALTURA_TELA // 4
    for linha in instrucoes:
        texto_linha = FONTE_ALTERNATIVA.render(linha, True, BRANCO)
        texto_linha_rect = texto_linha.get_rect(center=(LARGURA_TELA // 2, y_pos))
        TELA.blit(texto_linha, texto_linha_rect)
        y_pos += 40 # Espaçamento entre as linhas

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: # Tecla ESC para voltar
                estado_atual_jogo = GAME_STATE_MENU # Volta para o menu
                return True
    return True

# --- Loop Principal do Jogo ---
running = True 
clock = pygame.time.Clock()

# ATENÇÃO: Define o estado inicial para o MENU
estado_atual_jogo = GAME_STATE_MENU 

while running:
    # --- Tratamento de Eventos Gerais (Fechar Janela) ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- Lógica do Jogo (Baseada no Estado Atual) ---
    if estado_atual_jogo == GAME_STATE_MENU:
        running = tela_menu_inicial()
        # Se o estado mudou para PLAYING aqui, é porque o botão "Iniciar Jogo" foi clicado
        if estado_atual_jogo == GAME_STATE_PLAYING:
            # Só inicia o jogo de fato quando sair do menu
            fase_atual_idx = 0 
            carregar_recursos_fase() 
            # NOVO: Recarrega as perguntas disponíveis do banco de dados completo e embaralha
            perguntas_restantes = list(PERGUNTAS) # Cria uma cópia da lista original
            random.shuffle(perguntas_restantes) # Embaralha as perguntas para que a ordem seja aleatória a cada novo jogo
            iniciar_nova_rodada() 
            
    elif estado_atual_jogo == GAME_STATE_HOW_TO_PLAY:
        running = tela_como_jogar()
    elif estado_atual_jogo == GAME_STATE_END_GAME:
        running = tela_fim_de_jogo()
        # Ao reiniciar do Game Over, a tela_fim_de_jogo já cuida de resetar perguntas_restantes se 'R' for pressionado
    else: # Estados de jogo ativo: PLAYING, SHOW_MESSAGE, TRANSITION, OBSTACLE_COLLISION_PAUSE
        # --- Lógica de Movimento Contínuo do Carro e Rotação Visual ---
        if estado_atual_jogo == GAME_STATE_PLAYING: # O carro só se move no estado de jogo normal
            keys = pygame.key.get_pressed() 
            
            movendo_esquerda = False
            movendo_direita = False

            if keys[pygame.K_LEFT]:
                carro_x -= VELOCIDADE_CARRO
                movendo_esquerda = True
            if keys[pygame.K_RIGHT]:
                carro_x += VELOCIDADE_CARRO
                movendo_direita = True
            
            # Atualiza o estado de rotação do carro
            if movendo_esquerda:
                carro_rotacao_estado = "esquerda"
            elif movendo_direita:
                carro_rotacao_estado = "direita"
            else:
                carro_rotacao_estado = "reto" # Volta para a posição reta se nenhuma seta estiver pressionada
                
            # Limitar o carro à área da pista
            if carro_x < LARGURA_TELA // 4:
                carro_x = LARGURA_TELA // 4
            if carro_x > LARGURA_TELA * 3 // 4 - LARGURA_CARRO:
                carro_x = LARGURA_TELA * 3 // 4 - LARGURA_CARRO
                
        if estado_atual_jogo == GAME_STATE_PLAYING or estado_atual_jogo == GAME_STATE_TRANSITION or estado_atual_jogo == GAME_STATE_OBSTACLE_COLLISION_PAUSE:
            mover_elementos_fase() # Move os elementos da fase (portões ou obstáculos)

        # --- Desenho (Baseada no Estado Atual) ---
        TELA.fill(PRETO) # Limpa a tela com fundo preto

        # Desenha os elementos do jogo nos estados PLAYING, SHOW_MESSAGE, TRANSITION, OBSTACLE_COLLISION_PAUSE
        desenhar_pista()
        desenhar_carro(carro_x, carro_y)
        
        fase = FASES[fase_atual_idx] # Obtém a fase atual para decidir o que desenhar
        if fase["tipo"] == "quiz":
            desenhar_portoes() # Desenha portões apenas se for fase de quiz
        elif fase["tipo"] == "obstaculos":
            desenhar_obstaculos() # Desenha obstáculos apenas se for fase de obstáculos

        desenhar_pergunta() 
        desenhar_pontuacao() 

        if estado_atual_jogo == GAME_STATE_SHOW_MESSAGE or estado_atual_jogo == GAME_STATE_OBSTACLE_COLLISION_PAUSE:
            exibir_mensagem() 

    pygame.display.flip() 

    clock.tick(60) 

# --- Fim do Jogo ---
pygame.quit() 
sys.exit()