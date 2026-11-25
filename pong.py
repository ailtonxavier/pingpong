import curses
import time
import random
import lgpio

# 1. Configuração do chip GPIO e dos 4 botões com Pull-Up interno
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

def main(stdscr):
    # Configurações do terminal curses
    curses.curs_set(0)          # Esconde o cursor piscando
    stdscr.nodelay(True)        # Não trava o loop esperando tecla do teclado
    stdscr.timeout(0)

    altura, largura = stdscr.getmaxyx()

    # Garante um tamanho mínimo de janela caso o terminal esteja muito pequeno
    if altura < 15 or largura < 40:
        raise RuntimeError("Aumente a janela do terminal (minimo 40x15).")

    # Dimensões das raquetes (em linhas de texto)
    raquete_alt = max(3, altura // 5)
    p1_y = altura // 2 - raquete_alt // 2
    p2_y = altura // 2 - raquete_alt // 2
    p1_x = 2
    p2_x = largura - 3

    # Posição e velocidade da bola
    bola_x = float(largura // 2)
    bola_y = float(altura // 2)
    vel_x = 0.8 * random.choice((1, -1))
    vel_y = 0.4 * random.choice((1, -1))

    placar_p1 = 0
    placar_p2 = 0

    def reiniciar_bola():
        nonlocal bola_x, bola_y, vel_x, vel_y
        bola_x = float(largura // 2)
        bola_y = float(altura // 2)
        vel_x = 0.8 * random.choice((1, -1))
        vel_y = 0.4 * random.choice((1, -1))

    while True:
        # Permite sair apertando 'q' ou 'ESC' no teclado
        tecla = stdscr.getch()
        if tecla in (ord('q'), ord('Q'), 27):
            break

        # Leitura dos botões físicos (0 == pressionado por causa do PULL_UP)
        if lgpio.gpio_read(h, PIN_P1_CIMA) == 0 and p1_y > 1:
            p1_y -= 1
        if lgpio.gpio_read(h, PIN_P1_BAIXO) == 0 and p1_y + raquete_alt < altura - 1:
            p1_y += 1

        if lgpio.gpio_read(h, PIN_P2_CIMA) == 0 and p2_y > 1:
            p2_y -= 1
        if lgpio.gpio_read(h, PIN_P2_BAIXO) == 0 and p2_y + raquete_alt < altura - 1:
            p2_y += 1

        # Atualiza posição da bola
        bola_x += vel_x
        bola_y += vel_y

        bx = int(round(bola_x))
        by = int(round(bola_y))

        # Rebater no teto e no chão
        if by <= 1:
            by = 1