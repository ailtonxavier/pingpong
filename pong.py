import pygame
import random
import lgpio

# 1. Configuração do chip GPIO e dos 4 botões com Pull-Up interno
# Em Raspberry Pi 3/4 geralmente é chip 0; no Raspberry Pi 5 geralmente é chip 4.
try:
    h = lgpio.gpiochip_open(0)
except lgpio.error:
    h = lgpio.gpiochip_open(4)

PIN_P1_CIMA = 17
PIN_P1_BAIXO = 27
PIN_P2_CIMA = 22
PIN_P2_BAIXO = 23

BOTOES = [PIN_P1_CIMA, PIN_P1_BAIXO, PIN_P2_CIMA, PIN_P2_BAIXO]

for pino in BOTOES:
    lgpio.gpio_claim_input(h, pino, lgpio.SET_PULL_UP)

# 2. Inicialização do Pygame
pygame.init()
LARGURA, ALTURA = 800, 600
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Pong lgpio - Raspberry Pi")
relogio = pygame.time.Clock()
fonte = pygame.font.SysFont("monospace", 50, bold=True)

# Cores
PRETO = (15, 15, 20)
BRANCO = (240, 240, 240)
VERDE = (50, 220, 120)

# Raquetes e Bola
RAQUETE_L, RAQUETE_A = 15, 100
VEL_RAQUETE = 8
p1 = pygame.Rect(30, ALTURA // 2 - RAQUETE_A // 2, RAQUETE_L, RAQUETE_A)
p2 = pygame.Rect(LARGURA - 30 - RAQUETE_L, ALTURA // 2 - RAQUETE_A // 2, RAQUETE_L, RAQUETE_A)

bola = pygame.Rect(LARGURA // 2 - 10, ALTURA // 2 - 10, 20, 20)
vel_bola_x = 6 * random.choice((1, -1))
vel_bola_y = 6 * random.choice((1, -1))

placar_p1 = 0
placar_p2 = 0

def reiniciar_bola():
    global vel_bola_x, vel_bola_y
    bola.center = (LARGURA // 2, ALTURA // 2)
    vel_bola_x = 6 * random.choice((1, -1))
    vel_bola_y = 6 * random.choice((1, -1))

# 3. Loop Principal do Jogo
rodando = True
try:
    while rodando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                rodando = False

        # Leitura dos botões físicos (0 == pressionado, 1 == solto por causa do PULL_UP)
        if lgpio.gpio_read(h, PIN_P1_CIMA) == 0 and p1.top > 0:
            p1.y -= VEL_RAQUETE
        if lgpio.gpio_read(h, PIN_P1_BAIXO) == 0 and p1.bottom < ALTURA:
            p1.y += VEL_RAQUETE

        if lgpio.gpio_read(h, PIN_P2_CIMA) == 0 and p2.top > 0:
            p2.y -= VEL_RAQUETE
        if lgpio.gpio_read(h, PIN_P2_BAIXO) == 0 and p2.bottom < ALTURA:
            p2.y += VEL_RAQUETE

        # Movimento da bola
        bola.x += vel_bola_x
        bola.y += vel_bola_y

        # Rebater no teto e no chão
        if bola.top <= 0 or bola.bottom >= ALTURA:
            vel_bola_y *= -1

        # Rebater nas raquetes (aumenta levemente a velocidade a cada batida)
        if bola.colliderect(p1) and vel_bola_x < 0:
            vel_bola_x = -vel_bola_x * 1.05
        if bola.colliderect(p2) and vel_bola_x > 0:
            vel_bola_x = -vel_bola_x * 1.05

        # Pontuação
        if bola.left <= 0:
            placar_p2 += 1
            reiniciar_bola()
        if bola.right >= LARGURA:
            placar_p1 += 1
            reiniciar_bola()

        # Desenho na tela
        tela.fill(PRETO)
        pygame.draw.aaline(tela, (80, 80, 90), (LARGURA // 2, 0), (LARGURA // 2, ALTURA))
        pygame.draw.rect(tela, BRANCO, p1, border_radius=4)
        pygame.draw.rect(tela, BRANCO, p2, border_radius=4)
        pygame.draw.ellipse(tela, VERDE, bola)

        texto_p1 = fonte.render(str(placar_p1), True, BRANCO)
        texto_p2 = fonte.render(str(placar_p2), True, BRANCO)
        tela.blit(texto_p1, (LARGURA // 4, 20))
        tela.blit(texto_p2, (LARGURA * 3 // 4, 20))

        pygame.display.flip()
        relogio.tick(60)

finally:
    # Libera os pinos e fecha o chip GPIO ao sair para não travar na próxima execução
    for pino in BOTOES:
        lgpio.gpio_free(h, pino)
    lgpio.gpiochip_close(h)
    pygame.quit()