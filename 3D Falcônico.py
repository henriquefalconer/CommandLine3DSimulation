import numpy as np
from PIL import Image
from math import cos, sin, pi
from os import system
from sys import stdin
from termios import tcgetattr, tcsetattr, TCSADRAIN
from tty import setraw


def getch():
    """Recebe e retorna um caractere digitado pelo usuário, sem ser necessário apertar 'enter'."""
    fd = stdin.fileno()
    old_settings = tcgetattr(fd)
    try:
        setraw(stdin.fileno())
        ch = stdin.read(1)
    finally:
        tcsetattr(fd, TCSADRAIN, old_settings)
    return ch


def centralize(string, centralize_vertically=True, page_width=None, page_height=None):
    """Recebe e imprime uma string, centralizando cada uma de suas linhas."""
    lines_string = string.split("\n")
    if page_width is None:
        page_width = 135
    if page_height is None:
        page_height = 40
    if centralize_vertically:
        print("\n"*int((page_height-len(lines_string))/2))
    for l in lines_string:
        space = int((page_width - len(l)) / 2)
        print(space * " " + l)


def rotacionar_ponto_x(x, y, teta):
    """A partir das coordenadas x e y de um ponto, retorna a componente x do mesmo ponto, porém utilizando-se
    como referência a rotação dos eixos por 'teta', no sentido anti-horário."""
    return x * cos(teta) - y * sin(teta)


def rotacionar_ponto_y(x, y, teta):
    """A partir das coordenadas x e y de um ponto, retorna a componente y do mesmo ponto, porém utilizando-se
    como referência a rotação dos eixos por 'teta', no sentido anti-horário."""
    return x * sin(teta) + y * cos(teta)


def projecao_do_segmento_no_plano(segmento, teta_1, teta_2):
    """Calcula e retorna as coordenadas da projeção das extremidades de um segmento tridimensional em um plano, o qual
    passa pela origem do espaço 3D e possui ângulos de rotação 'teta_1' e 'teta_2'."""
    # Rotacionar o plano de projeção em torno do eixo 'z', utilizando-se 'teta_1':
    seg_1_i = [rotacionar_ponto_x(seg[0], seg[1], teta_1) for seg in segmento]
    seg_1_j = [rotacionar_ponto_y(seg[0], seg[1], teta_1) for seg in segmento]
    seg_1_k = [seg[2] for seg in segmento]
    segmento_rotacao_1 = [[seg_1_i[n], seg_1_j[n], seg_1_k[n]] for n in range(0, 2)]
    # Rotacionar o eixo de projeção em torno do eixo 'i', utilizando-se 'teta_2':
    seg_2_i = [seg[0] for seg in segmento_rotacao_1]
    seg_2_j = [rotacionar_ponto_x(seg[1], seg[2], teta_2) for seg in segmento_rotacao_1]
    seg_2_k = [rotacionar_ponto_y(seg[1], seg[2], teta_2) for seg in segmento_rotacao_1]
    segmento_rotacao_2 = [[seg_2_i[n], seg_2_j[n], seg_2_k[n]] for n in range(0, 2)]
    # Projeção das extremidades do segmento tridimensional no plano rotacionado:
    projecao_vetor_no_plano = [[seg[0], seg[2]] for seg in segmento_rotacao_2]
    return projecao_vetor_no_plano


def coordenadas_continuas_de_segmento_bidimensional(segmento, quantidade):
    """A partir das coordenadas das extremidades de um segmento bidimensional, retorna uma quantidade de
    coordenadas que correspondem com os pontos entre as próprias extremidades."""
    lista_coordenadas = []
    coordenadas_x = np.linspace(segmento[0][0], segmento[1][0], quantidade)
    coordenadas_y = np.linspace(segmento[0][1], segmento[1][1], quantidade)
    for c in range(0, quantidade):
        lista_coordenadas.append([coordenadas_x[c], coordenadas_y[c]])
    return lista_coordenadas


def verificacao_de_lista(x, y, coordenadas):
    """Verifica, com um grau de incerteza, se um ponto (x, y) está em uma lista de coordenadas."""
    incerteza = .5
    for c in coordenadas:
        if (abs(c[0] - x) <= incerteza) and (abs(c[1] - y) <= incerteza):
            return True
    return False


def imprimir_interface(x_min, x_max, y_min, y_max, coordenadas):
    """A partir de uma lista de coordenadas, imprime o gráfico do conjunto de pontos dado."""
    y = y_max  # Tamanho vertical da tela de impressão
    string_total = "\n"
    while y >= y_min:
        string_linha = str(y) + " " * (6 - len(str(y)))
        x = x_min
        while x <= x_max:
            if verificacao_de_lista(x, y, coordenadas):
                string_linha += "*"
            elif abs(x) < .5:
                string_linha += "|"
            else:
                string_linha += " "
            x += .5
        string_total += string_linha + "\n"
        y -= 1
    centralize(string_total, True, 130)


def coordenadas_para_imagem(coordenadas):
    dados = np.ones((X_max-X_min, Y_max-Y_min, 3), dtype=np.uint8)*255
    color = False
    if color:
        for y in range(Y_max-Y_min):
            for x in range(X_max-X_min):
                dados[x, y] = [int(x/22-15)**2, int(x/22-9)**2, int(x/22-3)**2]
    for c in coordenadas:
        dados[int(c[1]-X_min), int(c[0]-Y_min)] = np.zeros(3)
    dados = dados[::-1]
    im = Image.fromarray(dados, 'RGB')
    im.save("my.png")
    im.show()


def funcionamento():
    view_manual = True
    page = 1
    while view_manual:
        system('clear')
        if page == 1:
            centralize("""
-------------------------------------------------------------------------------------------------------------
|                                                                                                           |
|                    COMO FUNCIONA O SISTEMA DE DEFINIÇÃO DE UM SEGMENTO TRIDIMENCIONAL:                    |
|                                                                                                           |
|  Para fins de simplicidade, o segmento em questão é definido pelas coordenadas de suas extremidades:      |
|                                                                                                           |
|                        'z' ^                                      'z' ^                                   |
|                            |  /                                       |  /                                |
|                       **   | /                                   *    | /                                 |
|                         ** |/          'i'           (i0, j0, k0)     |/          'i'                     |
|                -----------***---------->       ===>       ------------/----------->                       |
|                           /| **                                      /|                                   |
|                          / |   **                                   / |    *                              |
|                     'j' <  |                                   'j' <  |     (i1, j1, k1)                  |
|                                                                                                           |
|                                                                                                           |
|  Segmento = [[i0, j0, k0], [i1, j1, k1]] (0 -> "primeira extremidade"; 1 -> "segunda extremidade").       |
|                                                                                                           |
|  Ex.: Segmento = [[-4, 3, 5], [9, 20, -4.3]].                                                             |
|                                                                                                    Pág. 1 |
-------------------------------------------------------------------------------------------------------------
""")
        if page == 2:
            centralize("""
-------------------------------------------------------------------------------------------------------------
|                                                                                                           |
|                       COMO FUNCIONA O SISTEMA DE DEFINIÇÃO DO PLANO DE PROJEÇÃO:                          |
|                                                                                                           |
|  Primeiramente, o plano bidimensional é posto paralelo aos eixos 'i' e 'z', e ortogonal a 'j':            |
|                                                                                                           |
|                        'z' ^                                          ^ 'z'                               |
|                       -----|--/--                                -----|-----                              |
|                       |    | /  |                                |    |    |                              |
|                       |    |/   |      'i'                       |    |    |      'i'                     |
|                -------|----/----|------>       ===>       -------|----|----|------->                      |
|                       |   /|    |                                |    |    |                              |
|                       |  / |    |                                |    |    |                              |
|                       --/--|-----                                -----|-----                              |
|                    'j' <   |                                          |                                   |
|                                                                                                           |
|  Ao utilizar as teclas 'A' e 'D' do teclado, o usuário pode rotacionar o plano em torno do eixo 'z'.      |
|                                                                                                           |
|  De mesmo modo, com as teclas 'W' e 'S', o usuário pode rotacionar o plano em torno do eixo 'i'.          |
|                                                                                                    Pág. 2 |
-------------------------------------------------------------------------------------------------------------
""")
        if page == 3:
            centralize("""
-------------------------------------------------------------------------------------------------------------
|                                                                                                           |
|               COMO FUNCIONA O SISTEMA DE PROJEÇÃO DAS EXTREMIDADES DE UM SEGMENTO NO PLANO:               |
|                                                                                                           |
|  Sabendo-se as coordenadas das extremidades do segmento, assim como a posição do plano, cria-se as        |
|  coordenadas relativas ao plano de projeção (i0', j0', k0') e (i1', j1', k1'), eliminando-se de cada      |
|  coordenada a componente 'j'', de modo a projetar a região do espaço tridimensional em duas dimensões:    |
|                                                                                                           |
|                         'z'' ^                              (i0', k0')  ^ 'z''                            |
|                         –––––|––/––                                –––––|–––––                            |
|         (i0', j0', k0') | *  | /  |                                |*   |    |                            |
|                         |    |/   |      'i''                      |    |    |      'i''                  |
|                  –––––––|––––/––––|––––––>       ===>       ––––-––|––––|––––|––––––>                     |
|                         |   /|    |                                |    |    |                            |
|                         |  / |*   |                                |    |  * |                            |
|                         ––/––|–––––                                –––––|–––––                            |
|                     'j'' <   | (i1', j1', k1')                          | (i1', k1')                      |
|                                                                                                           |
|                                                                                                           |
|                                                                                                    Pág. 3 |
-------------------------------------------------------------------------------------------------------------
""")
        if page == 4:
            centralize("""
-------------------------------------------------------------------------------------------------------------
|                                                                                                           |
|                  COMO FUNCIONA O SISTEMA DE IMPRESSÃO DOS SEGMENTOS PROJETADOS NO PLANO:                  |
|                                                                                                           |
|  Pelas coodenadas das extremidades do segmento projetadas no plano, são criados outros pontos do          |
|  segmento em questão, de modo a devidamente representar-se o segmento:                                    |
|                                                                                                           |
|                        (i0', k0')  ^ 'z''            (i0', k0')  ^ 'z''                                   |
|                               –––––|–––––                   –––––|–––––                                   |
|                               |*   |    |                   |*   |    |                                   |
|                               |    |    |                   | ** |    |                                   |
|                               |    |    |       ===>        |   **    |                                   |
|                               |    |    |                   |    |**  |                                   |
|                               |    |  * |                   |    |  * |                                   |
|                               –––––|–––––                   –––––|–––––                                   |
|                                    | (i1', k1')                  | (i1', k1')                             |
|                                                                                                           |
|  Por praticidade, apenas o eixo 'z'' é exibido na impressão final.                                        |
|                                                                                                           |
|                                                                                                    Pág. 4 |
-------------------------------------------------------------------------------------------------------------
""")
        centralize("[A] -> Página anterior   [D] -> Página seguinte   [Q] -> Sair", False)
        alter_page = getch().lower()
        if (alter_page == "a") and (1 < page <= 4):
            page -= 1
        if (alter_page == "d") and (1 <= page < 4):
            page += 1
        if alter_page == "q":
            view_manual = False


# Variáveis de início:
Start = True
Debug = False
Selection = True
Print = False
Scale = 10
Speed = 0.025
# Loop principal do programa:
while True:
    # Recebimento de dados pelo usuário:
    while Selection:
        Selection = False
        if Start:
            Start = False
            system('clear')
            centralize("""\n
* * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
* ------------------------------------------------------- *
* ------ SEJA BEM-VINDO À SIMULAÇÃO FALCÔNICA 3D! ------- *
* ------------------------------------------------------- *
* * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
* ------------------------------------------------------- *
* --- Escolha um dos itens a seguir para a simulação: --- *
* ------------------------------------------------------- *
* * * * * * * * * * * * * * * * * * * * * * * * * * * * * *\n""")
            centralize("""\n[C] -> Cubo   [T] -> Tetraedro   [F] -> Funcionamento   [Q] -> Sair""", False)
            Objeto = getch().lower()
        # Seleção de objeto tridimensional da base de dados:
        Segmentos = []
        if Objeto == "c":  # Cubo.
            Tamanho_aresta = 20
            t = Tamanho_aresta / 2
            for i in [t, -t]:
                for j in [t, -t]:
                    Segmentos.append([[i, j, t], [i, j, -t]])
            for i in [t, -t]:
                for k in [t, -t]:
                    Segmentos.append([[i, t, k], [i, -t, k]])
            for j in [t, -t]:
                for k in [t, -t]:
                    Segmentos.append([[t, j, k], [-t, j, k]])
            # Definição da rotação inicial do plano de projeção:
            Rotacao_1 = .31
            Rotacao_2 = .15
            # Estabelecimento dos limites do plano de projeção:
            X_min = -20
            X_max = 20
            Y_min = -20
            Y_max = 20
            Quantidade = 15
        elif Objeto == "t":  # Tetraedro.
            Tamanho_aresta = 10
            t = 3 ** (1 / 2) * Tamanho_aresta
            Coordenadas_base = [[0, t, (1-3**(1/2))*t], [-3**(1/2)*t/2, -t/2, (1-3**(1/2))*t],
                                [3**(1/2)*t/2, -t/2, (1-3**(1/2))*t]]
            for i in Coordenadas_base:
                Segmentos.append([[0, 0, (2 ** (1 / 2) - 2 ** (1 / 2) + 1) * t], i])
            for i in range(-1, 2):
                Segmentos.append([Coordenadas_base[i], Coordenadas_base[i + 1]])
            # Definição da rotação inicial do plano de projeção:
            Rotacao_1 = 0
            Rotacao_2 = -.1
            # Estabelecimento dos limites do plano de projeção:
            X_min = -20
            X_max = 20
            Y_min = -21
            Y_max = 18
            Quantidade = 20
        elif Objeto == "f":
            funcionamento()
            Selection = True
            Start = True
        elif Objeto == "q":
            print()
            exit()
        else:
            Selection = True
            Start = True
    # Cálculo e impressão dos segmentos tridimensionais projetados no plano bidimensional:
    Render = True
    while Render:
        # Definição das coordenadas da projeção dos pontos pertencentes a cada um dos segmentos dados:
        Coordenadas = []
        if Print:
            X_min, X_max, Y_min, Y_max, Quantidade = X_min*Scale, X_max*Scale, Y_min*Scale, Y_max*Scale, Quantidade*1000
            Segmentos = [[[i*10 for i in j] for j in k] for k in Segmentos]
        for s in Segmentos:
            Extremidades_s_plano_projecao = projecao_do_segmento_no_plano(s, pi * Rotacao_1, pi * Rotacao_2)
            Coordenadas_s = coordenadas_continuas_de_segmento_bidimensional(Extremidades_s_plano_projecao, Quantidade)
            for i in Coordenadas_s: Coordenadas.append(i)
        # Impressão do plano de projeção:
        system('clear')
        if Print:
            coordenadas_para_imagem(Coordenadas)
            X_min, X_max, Y_min, Y_max, Quantidade = int(X_min / Scale), int(X_max / Scale), int(Y_min / Scale), int(Y_max / Scale), int(Quantidade / 1000)
            Segmentos = [[[int(i/10) for i in j] for j in k] for k in Segmentos]
        else:
            imprimir_interface(X_min, X_max, Y_min, Y_max, Coordenadas)
        if Debug:
            Rot_1_d = Rotacao_1*180
            Rot_2_d = Rotacao_2*180
            print("Rotação em torno do eixo 'z': %.2fº;\nRotação em torno do eixo 'i': %.2fº.\n" % (Rot_1_d, Rot_2_d))
        centralize("[W/A/S/D] -> Movimento | [R] -> Reposicionar | [P] -> Imprimir | [Q] -> Sair", False)
        # Modificações geradas pela interação do usuário:
        if not Print: Register = True
        Print = False
        while Register:
            Register = False
            Button = getch().lower()
            if Button == "w":
                Rotacao_2 -= Speed
            elif Button == "a":
                Rotacao_1 -= Speed
            elif Button == "s":
                Rotacao_2 += Speed
            elif Button == "d":
                Rotacao_1 += Speed
            elif Button == "r":
                Render = False
                Selection = True
            elif Button == "z":
                Debug = not Debug
            elif Button == "p":
                Print = True
            elif Button == "q":
                Render = False
                Selection = True
                Start = True
            else:
                Register = True
