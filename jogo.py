import cv2
import mediapipe as mp
import pygame
import random
import sys

# Inicializa o MediaPipe
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# Inicializa o OpenCV
cap = cv2.VideoCapture(0)

# Configurações iniciais da câmera
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Ajuste a largura desejada
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # Ajuste a altura desejada

# Inicializa o Pygame
pygame.init()
game_width, game_height = 800, 600
gameDisplay = pygame.display.set_mode((game_width, game_height))
pygame.display.set_caption('EXERGAME - PEGA BARATA')

# Cores
white = (255, 255, 255)
black = (0, 0, 0)

# Configurações do ícone (barata)
icon_size = 100  # Ajuste o tamanho desejado
icon_image = pygame.image.load('barata.png') 
icon_image = pygame.transform.scale(icon_image, (icon_size, icon_size))
icon_position = [random.randint(0, game_width - icon_size), random.randint(0, game_height - icon_size)]

# Configurações do jogador (mão)
hand_size = 130  # Tamanho da imagem da mão
hand_image = pygame.image.load('CHINELO.png') 
hand_image = pygame.transform.scale(hand_image, (hand_size, hand_size))
hand_position = (0, 0)

# Configuração do cronômetro
tempo_maximo = 7  
tempo_decorrido = 0
cronometro_iniciado = False

# Configuração inicial da pontuação
pontuacao = 0

# Função para verificar colisão entre a mão e a barata
def verificar_colisao(posicao_mao, posicao_fruta, tamanho_fruta):
    x_mao, y_mao = posicao_mao
    x_fruta, y_fruta = posicao_fruta

    return (
        x_mao <= x_fruta <= x_mao + hand_size and y_mao <= y_fruta <= y_mao + hand_size
    )

# Função para mostrar a pontuação e o tempo na tela
def mostrar_pontuacao_e_tempo(tempo_restante):
    fonte = pygame.font.SysFont(None, 40)
    texto_pontuacao = fonte.render(f'Pontuação: {pontuacao}', True, white)
    texto_tempo = fonte.render(f'Tempo: {tempo_restante}s', True, white)
    gameDisplay.blit(texto_pontuacao, (10, 10))
    gameDisplay.blit(texto_tempo, (10, 50))

# Função para encerrar o jogo e exibir a mensagem de derrota
def encerrar_jogo():
    gameDisplay.fill(black)
    fonte = pygame.font.SysFont(None, 60)
    texto_perdeu = fonte.render('VOCÊ PERDEU', True, white)
    texto_pontuacao = fonte.render(f'Pontuação: {pontuacao}', True, white)
    gameDisplay.blit(texto_perdeu, (game_width // 2 - 150, game_height // 2 - 50))
    gameDisplay.blit(texto_pontuacao, (game_width // 2 - 150, game_height // 2 + 50))
    pygame.display.update()
    pygame.time.delay(3000)  # Aguarda 3 segundos antes de encerrar
    pygame.quit()
    cap.release()
    cv2.destroyAllWindows()
    sys.exit()

# Função para exibir o menu inicial
def menu_inicial():
    menu_ativo = True

    while menu_ativo:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                cap.release()
                cv2.destroyAllWindows()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return True  # Modo com a câmera
                elif event.key == pygame.K_2:
                    return False  # Modo com background

        gameDisplay.fill(black)
        fonte = pygame.font.SysFont(None, 60)
        texto_titulo = fonte.render('Escolha o Modo de Jogo:', True, white)
        texto_opcao1 = fonte.render('1 - Câmera ao Vivo', True, white)
        texto_opcao2 = fonte.render('2 - Background', True, white)

        gameDisplay.blit(texto_titulo, (game_width // 2 - 200, game_height // 2 - 100))
        gameDisplay.blit(texto_opcao1, (game_width // 2 - 150, game_height // 2))
        gameDisplay.blit(texto_opcao2, (game_width // 2 - 150, game_height // 2 + 50))

        pygame.display.update()

# Executa o menu inicial
modo_camera = menu_inicial()

# Loop principal
with mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Erro ao capturar o quadro.")
            break

        # Inverte apenas horizontalmente
        frame = cv2.flip(frame, 0)

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                hand_x = int(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * game_width)
                hand_y = int((1 - hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y) * game_height)
                hand_position = (hand_x - hand_size // 2, hand_y - hand_size // 2)

                # Se a mão tocar na barata, adicione pontuação e reinicie o jogo
                if verificar_colisao(hand_position, icon_position, icon_size):
                    pontuacao += 1
                    icon_position = [random.randint(0, game_width - icon_size), random.randint(0, game_height - icon_size)]
                    tempo_decorrido = 0  # Reinicia o cronômetro

        if modo_camera:
            # Desenha o frame da câmera como background
            image_surface = pygame.surfarray.make_surface(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            gameDisplay.blit(image_surface, (0, 0))
        else:
            # Modo com background
            background_image = pygame.image.load('background.jpg') 
            background_image = pygame.transform.scale(background_image, (game_width, game_height))
            gameDisplay.blit(background_image, (0, 0))

        # Desenha a barata na tela
        gameDisplay.blit(icon_image, icon_position)

        # Desenha a imagem da mão na tela
        gameDisplay.blit(hand_image, hand_position)

        # Mostra a pontuação e o tempo
        mostrar_pontuacao_e_tempo(tempo_maximo - tempo_decorrido)

        # Inicia o cronômetro quando a barata.png aparece pela primeira vez
        if not cronometro_iniciado:
            pygame.time.set_timer(pygame.USEREVENT, 1000)  # Configura um evento de temporizador a cada 1 segundo
            cronometro_iniciado = True

        # Atualiza o cronômetro
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                cap.release()
                cv2.destroyAllWindows()
                sys.exit()
            elif event.type == pygame.USEREVENT:
                tempo_decorrido += 1
                if tempo_decorrido >= tempo_maximo:
                    encerrar_jogo()

        pygame.display.update()
