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
pygame.display.set_caption("Jogo de Perguntas e Respostas de Carro")

# --- Cores ---
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
CINZA = (100, 100, 100)
VERDE = (0, 200, 0)
VERMELHO = (200, 0, 0)
AZUL = (0, 0, 200)
AMARELO = (255, 255, 0) # Para as linhas da pista
CIANO = (0, 255, 255) # Para o texto de vidas

# --- Fontes ---
FONTE_PERGUNTA = pygame.font.Font(None, 40)
FONTE_ALTERNATIVA = pygame.font.Font(None, 30)
FONTE_MENSAGEM = pygame.font.Font(None, 60)
FONTE_PONTUACAO = pygame.font.Font(None, 35)


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
        "duracao_fase_obstaculo": 10000, 
        "intervalo_geracao_obstaculo_min": 240, 
        "intervalo_geracao_obstaculo_max": 480, 
        "pista_imagem": "img_pista_espaco.png", 
        "carro_reto_imagem": "img_navefrente.png", 
        "carro_esquerda_imagem": "img_naveesquerda.png",
        "carro_direita_imagem": "img_navedireita.png",
        "obstaculo_imagem": "img_meteoro.png", 
        "velocidade_obstaculo": 7 
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
        "carro_direita_imagem": "img_carromardireita.png"
    }
]

# --- Variáveis Globais do Jogo (estado atual) ---
carro_x = POS_INICIAL_CARRO_X
carro_y = POS_INICIAL_CARRO_Y
pista_y_offset = 0 # Para simular o movimento da pista

portoes = [] 
obstaculos = [] 

pergunta_atual_idx = 0
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
    global pergunta_ativa, portoes, pergunta_atual_idx, pode_escolher, estado_atual_jogo, vidas_restantes, carro_rotacao_estado
    global obstaculos, tempo_inicio_fase_obstaculo, proximo_obstaculo_tempo # NOVO

    fase = FASES[fase_atual_idx]

    # PRIORIDADE: Lógica de Fim de Jogo (vidas zeradas ou perguntas de quiz esgotadas se for fase de quiz)
    if vidas_restantes <= 0:
        estado_atual_jogo = GAME_STATE_END_GAME
        return
    if fase["tipo"] == "quiz" and pergunta_atual_idx >= len(PERGUNTAS):
        estado_atual_jogo = GAME_STATE_END_GAME
        return

    # Limpa elementos da fase anterior
    portoes = []
    obstaculos = []
    carro_rotacao_estado = "reto" # Resetar rotação do carro para a nova rodada/fase

    if fase["tipo"] == "quiz":
        pergunta_ativa = True
        pode_escolher = True
        
        pergunta_obj = PERGUNTAS[pergunta_atual_idx]
        
        # Validação: Garante que a pergunta está bem formatada
        if "alternativas" not in pergunta_obj or not isinstance(pergunta_obj["alternativas"], list) or len(pergunta_obj["alternativas"]) < 2:
            print(f"Erro: Pergunta {pergunta_atual_idx} em perguntas_banco.py está malformada. Encerrando jogo.")
            estado_atual_jogo = GAME_STATE_END_GAME
            return

        alternativas_shuffled = list(pergunta_obj["alternativas"])
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
        
    estado_atual_jogo = GAME_STATE_PLAYING # Define o estado como PLAYING no final da configuração da rodada

def desenhar_portoes():
    for portao in portoes:
        if IMAGEM_PORTAO:
            # Centraliza a imagem do portão dentro do seu retângulo de colisão
            img_rect = IMAGEM_PORTAO.get_rect(center=portao["rect"].center)
            TELA.blit(IMAGEM_PORTAO, img_rect.topleft)
        else:
            # Desenha um retângulo verde para o portão se não houver imagem
            pygame.draw.rect(TELA, VERDE, portao["rect"])
        
        # Renderiza o texto da alternativa no centro do portão
        texto_superficie = FONTE_ALTERNATIVA.render(portao["texto"], True, PRETO)
        texto_ret = texto_superficie.get_rect(center=portao["rect"].center)
        TELA.blit(texto_superficie, texto_ret)

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
    global pergunta_atual_idx
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
                gerar_obstaculo() # Chamar gerar_obstaculo para criar um novo obstáculo
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
            carro_y = POS_INICIAL_CARRO_Y
            colidiu_com_portao_correto = False
            portao_correto_passado = None
            
            # Lógica de avanço de fase após transição de pergunta
            proxima_fase_existente = (fase_atual_idx + 1) < len(FASES)
            if vidas_restantes <= 0:
                estado_atual_jogo = GAME_STATE_END_GAME
            elif proxima_fase_existente and pontuacao >= FASES[fase_atual_idx + 1]["acertos_para_proxima"]:
                fase_atual_idx += 1 
                carregar_recursos_fase() 
                iniciar_nova_rodada() # Inicia a próxima fase (que pode ser de obstáculos)
                print(f"Parabéns! Avançando para: {FASES[fase_atual_idx]['nome']}")
                estado_atual_jogo = GAME_STATE_PLAYING # Volta ao estado de jogo normal
            else: # Se não há próxima fase ou acertos suficientes, apenas avança para a próxima pergunta (se houver)
                pergunta_atual_idx += 1 
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
    # TODAS as variáveis globais que são Lidas/MODIFICADAS dentro desta função DEVEM SER DECLARADAS AQUI.
    global fase_atual_idx 
    global pergunta_ativa 
    global portoes 
    global pergunta_atual_idx 
    global estado_atual_jogo 

    # Desenha a pergunta no topo da tela, apenas se estiver no estado de jogo e a fase for de quiz
    if FASES[fase_atual_idx]["tipo"] == "quiz" and pergunta_ativa and portoes:
        pergunta_texto = PERGUNTAS[pergunta_atual_idx]["pergunta"] 
        texto_superficie = FONTE_PERGUNTA.render(pergunta_texto, True, BRANCO) 
        texto_ret = texto_superficie.get_rect(center=(LARGURA_TELA // 2, 50))
        TELA.blit(texto_superficie, texto_ret)
    # Opcional: Mostrar o nome da fase ou uma mensagem genérica na fase de obstáculos
    elif FASES[fase_atual_idx]["tipo"] == "obstaculos" and estado_atual_jogo == GAME_STATE_PLAYING:
        texto_fase = FONTE_PERGUNTA.render(FASES[fase_atual_idx]["nome"], True, BRANCO)
        texto_ret = texto_fase.get_rect(center=(LARGURA_TELA // 2, 50))
        TELA.blit(texto_fase, texto_ret)

def exibir_mensagem():
    # TODAS as variáveis globais que serão MODIFICADAS dentro desta função DEVEM SER DECLARADAS AQUI.
    global mensagem_exibida
    global tempo_mensagem
    global pergunta_atual_idx
    global estado_atual_jogo
    global vidas_restantes
    global carro_x 
    global carro_y 
    global fase_atual_idx 

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
                    
                    if FASES[fase_atual_idx]["tipo"] == "quiz":
                        # Aumentamos pergunta_atual_idx apenas se for fase de quiz.
                        # Caso contrário, ela permanece a mesma (para a próxima fase de obstáculo, por exemplo).
                        pergunta_atual_idx += 1 
                    
                    iniciar_nova_rodada() 
                    estado_atual_jogo = GAME_STATE_PLAYING


def desenhar_pontuacao():
    texto_pontuacao = FONTE_PONTUACAO.render(f"Pontuação: {pontuacao}", True, BRANCO)
    TELA.blit(texto_pontuacao, (10, 10))

    texto_vidas = FONTE_PONTUACAO.render(f"Vidas: {vidas_restantes}", True, CIANO) # Exibe as vidas
    TELA.blit(texto_vidas, (10, 50)) # Posição abaixo da pontuação

def tela_fim_de_jogo():
    global estado_atual_jogo, pontuacao, pergunta_atual_idx, carro_x, carro_y, vidas_restantes
    global carro_rotacao_estado, fase_atual_idx 

    TELA.fill(PRETO) # Fundo preto para a tela de fim de jogo
    
    # Mensagens da tela de fim de jogo
    texto_fim = FONTE_MENSAGEM.render("Fim de Jogo!", True, BRANCO)
    texto_pontuacao_final = FONTE_MENSAGEM.render(f"Sua Pontuação Final: {pontuacao}", True, BRANCO)
    texto_reiniciar = FONTE_ALTERNATIVA.render("Pressione R para Reiniciar", True, BRANCO)

    # Posições das mensagens
    ret_fim = texto_fim.get_rect(center=(LARGURA_TELA // 2, ALTURA_TELA // 2 - 50))
    ret_pontuacao_final = texto_pontuacao_final.get_rect(center=(LARGURA_TELA // 2, ALTURA_TELA // 2 + 10))
    ret_reiniciar = texto_reiniciar.get_rect(center=(LARGURA_TELA // 2, ALTURA_TELA // 2 + 80))

    TELA.blit(texto_fim, ret_fim)
    TELA.blit(texto_pontuacao_final, ret_pontuacao_final)
    TELA.blit(texto_reiniciar, ret_reiniciar)

    pygame.display.flip() # Atualiza a tela para exibir as mensagens

    # Loop de eventos exclusivo para a tela de fim de jogo
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False # Se o usuário fechar a janela, o jogo deve parar
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                # Lógica para reiniciar o jogo
                pontuacao = 0          # Reseta a pontuação
                pergunta_atual_idx = 0       # Volta para a primeira pergunta
                carro_x = POS_INICIAL_CARRO_X # Reseta a posição X do carro
                carro_y = POS_INICIAL_CARRO_Y # Reseta a posição Y do carro
                vidas_restantes = TOTAL_VIDAS # Reseta as vidas
                carro_rotacao_estado = "reto" # Reseta a rotação do carro
                fase_atual_idx = 0             # Reinicia para a primeira fase
                # NOTA: carregar_recursos_fase() e iniciar_nova_rodada() serão chamadas pelo loop principal
                estado_atual_jogo = GAME_STATE_MENU # Volta para o menu ao reiniciar
                return True # Retorna True para continuar o loop principal do jogo (sair da tela de fim de jogo)
    return True # Retorna True para continuar o loop do jogo enquanto na tela de fim de jogo

def tela_menu_inicial():
    global estado_atual_jogo

    try:
        fundo_menu_img = pygame.image.load(os.path.join('..', 'imagens', 'img_menu_fundo.png'))
        fundo_menu_img = pygame.transform.scale(fundo_menu_img, (LARGURA_TELA, ALTURA_TELA))
    except pygame.error:
        print("Aviso: 'img_menu_fundo.png' não encontrada. Usando fundo preto para o menu.")
        fundo_menu_img = None

    titulo_texto = FONTE_MENSAGEM.render("", True, BRANCO)
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
        "Bem-vindo ao Quiz da Estrada!",
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
        # Para o caso de reiniciar do menu, ele já está tratando o ESCAPE no teclado para voltar
        # de "Como Jogar" e o R para reiniciar do "Fim de Jogo".

    # --- Lógica do Jogo (Baseada no Estado Atual) ---
    if estado_atual_jogo == GAME_STATE_MENU:
        running = tela_menu_inicial()
        # Se o estado mudou para PLAYING aqui, é porque o botão "Iniciar Jogo" foi clicado
        if estado_atual_jogo == GAME_STATE_PLAYING:
            # Só inicia o jogo de fato quando sair do menu
            fase_atual_idx = 0 
            carregar_recursos_fase() 
            iniciar_nova_rodada() 
    elif estado_atual_jogo == GAME_STATE_HOW_TO_PLAY:
        running = tela_como_jogar()
    elif estado_atual_jogo == GAME_STATE_END_GAME:
        running = tela_fim_de_jogo()
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