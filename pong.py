import curses
import time
import random

def main(stdscr):
    curses.curs_set(0)          # Esconde o cursor piscando
    stdscr.nodelay(True)        # Não trava o loop esperando tecla
    stdscr.keypad(True)         # Habilita a leitura das setas do teclado
    stdscr.timeout(0)

    altura, largura = stdscr.getmaxyx()

    if altura < 15 or largura < 40:
        raise RuntimeError("Aumente a janela do terminal (minimo 40x15).")

    raquete_alt = max(3, altura // 5)
    p1_y = altura // 2 - raquete_alt // 2
    ia_y = altura // 2 - raquete_alt // 2
    p1_x = 2
    ia_x = largura - 3

    bola_x = float(largura // 2)
    bola_y = float(altura // 2)
    vel_x = 0.8 * random.choice((1, -1))
    vel_y = 0.4 * random.choice((1, -1))

    placar_p1 = 0
    placar_ia = 0
    contador_ia = 0

    def reiniciar_bola():
        nonlocal bola_x, bola_y, vel_x, vel_y
        bola_x = float(largura // 2)
        bola_y = float(altura // 2)
        vel_x = 0.8 * random.choice((1, -1))
        vel_y = 0.4 * random.choice((1, -1))

    while True:
        tecla = stdscr.getch()
        if tecla in (ord('q'), ord('Q'), 27):
            break

        # Controles do Jogador 1 (Setas Cima e Baixo)
        if tecla == curses.KEY_UP and p1_y > 1:
            p1_y -= 1
        elif tecla == curses.KEY_DOWN and p1_y + raquete_alt < altura - 1:
            p1_y += 1

        # Atualiza posição da bola
        bola_x += vel_x
        bola_y += vel_y

        bx = int(round(bola_x))
        by = int(round(bola_y))

        # Rebater no teto e no chão
        if by <= 1:
            by = 1
            vel_y = abs(vel_y)
        elif by >= altura - 2:
            by = altura - 2
            vel_y = -abs(vel_y)

        # Movimento da IA (raquete da direita segue a bola com um leve atraso)
        contador_ia += 1
        if contador_ia % 2 == 0 and vel_x > 0:
            centro_ia = ia_y + raquete_alt // 2
            if centro_ia < by and ia_y + raquete_alt < altura - 1:
                ia_y += 1
            elif centro_ia > by and ia_y > 1:
                ia_y -= 1

        # Rebater na raquete do Jogador 1
        if bx <= p1_x + 1 and vel_x < 0:
            if p1_y <= by <= p1_y + raquete_alt:
                vel_x = min(abs(vel_x) * 1.05, 1.5)
                bx = p1_x + 1

        # Rebater na raquete da IA
        if bx >= ia_x - 1 and vel_x > 0:
            if ia_y <= by <= ia_y + raquete_alt:
                vel_x = -min(abs(vel_x) * 1.05, 1.5)
                bx = ia_x - 1

        # Pontuação
        if bx <= 0:
            placar_ia += 1
            reiniciar_bola()
        elif bx >= largura - 1:
            placar_p1 += 1
            reiniciar_bola()

        # Desenho no terminal
        stdscr.erase()
        stdscr.border()

        for y in range(1, altura - 1, 2):
            stdscr.addch(y, largura // 2, '|')

        placar_str = f" VOCE {placar_p1}   {placar_ia} CPU "
        stdscr.addstr(0, max(1, (largura - len(placar_str)) // 2), placar_str)

        for i in range(raquete_alt):
            if 1 <= p1_y + i < altura - 1:
                stdscr.addch(p1_y + i, p1_x, '#')
            if 1 <= ia_y + i < altura - 1:
                stdscr.addch(ia_y + i, ia_x, '#')

        if 1 <= by < altura - 1 and 1 <= bx < largura - 1:
            stdscr.addch(by, bx, 'O')

        stdscr.refresh()
        time.sleep(0.04)

curses.wrapper(main)