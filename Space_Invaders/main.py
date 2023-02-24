import pygame as py
import random as ra
import os
py.font.init()

largura, altura = 900, 900
win = py.display.set_mode((largura, altura))
py.display.set_caption('Space Shooter Python')
nave_amarela = py.image.load(os.path.join('Imagens', 'pixel_ship_yellow.png'))
nave_vermelha = py.image.load(os.path.join('Imagens', 'pixel_ship_red_small.png'))
nave_verde = py.image.load(os.path.join('Imagens', 'pixel_ship_green_small.png'))
nave_azul = py.image.load(os.path.join('Imagens', 'pixel_ship_blue_small.png'))
l_vermelho = py.image.load(os.path.join('Imagens', 'pixel_laser_red.png'))
l_azul = py.image.load(os.path.join('Imagens', 'pixel_laser_blue.png'))
l_amarelo = py.image.load(os.path.join('Imagens', 'pixel_laser_yellow.png'))
l_verde = py.image.load(os.path.join('Imagens', 'pixel_laser_green.png'))
fundo = py.transform.scale(py.image.load(os.path.join('Imagens', 'background-black.png')), (largura, altura))

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = py.mask.from_surface(self.img)

    def desenhar(self, janela):
        """
        Imprimir imagem na tela
        :param janela: janela criada
        :return: imagem na tela
        """
        janela.blit(self.img, (self.x, self.y))

    def mover(self, vel):
        """
        Mover pelo eixo y
        :param vel: velocidade do objeto
        :return: a velocidade pelo eixo y
        """
        self.y += vel

    def off_tela(self, altura):
        return not(self.y <= altura and self.y >= 0)

    def colisao(self, obj):
        return colidir(self, obj)


class Nave:
    cooldown = 30

    def __init__(self, x, y, vida=100):
        self.x = x
        self.y = y
        self.vida = vida
        self.img_nave = None
        self.img_laser = None
        self.lasers = []
        self.contador_cooldown = 0


    def desenhar(self, janela):
        janela.blit(self.img_nave, (self.x, self.y))
        for laser in self.lasers:
            laser.desenhar(janela)

    def mover_lasers(self, vel, obj):
        """
        Movimentação dos lasers
        :param vel: velocidade od laser
        :param obj: objeto que atira o laser
        :return: remove um item da lista 'lasers'
        """
        self.Cooldown()
        for laser in self.lasers:
            laser.mover(vel)
            if laser.off_tela(altura):
                self.lasers.remove(laser)
            elif laser.colisao(obj):
                obj.vida -= 10
                self.lasers.remove(laser)

    def Cooldown(self):
        if self.contador_cooldown >= self.cooldown:
            self.contador_cooldown = 0
        elif self.contador_cooldown > 0:
            self.contador_cooldown += 1

    def tiro(self):
        """
        Atira o laser
        :return: adiciona um item na lista 'lasers'
        """
        if self.contador_cooldown == 0:
            laser = Laser(self.x, self.y, self.img_laser)
            self.lasers.append(laser)
            self.contador_cooldown = 1

    def get_height(self):
        return self.img_nave.get_height()

    def get_width(self):
        return self.img_nave.get_width()


class Jogador(Nave):
    def __init__(self, x, y, vida=100):
        super().__init__(x, y, vida)
        self.img_nave = nave_amarela
        self.img_laser = l_amarelo
        self.mask = py.mask.from_surface(self.img_nave)
        self.vida_max = vida

    def mover_lasers(self, vel, objs):
        self.Cooldown()
        for laser in self.lasers:
            laser.mover(vel)
            if laser.off_tela(altura):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.colisao(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def desenhar(self, janela):
        super().desenhar(janela)
        self.barra_vida(janela)

    def barra_vida(self, janela):
        """
        Mostrar a barra de vida do jogador
        :param janela: janela na tela
        :return: peuqenas barras que diminuem conforme o jogador toma dano
        """
        py.draw.rect(janela, (255, 0, 0), (self.x, self.y + self.img_nave.get_height() + 10, self.img_nave.get_width(), 10))
        py.draw.rect(janela, (0, 255, 0), (self.x, self.y + self.img_nave.get_height() + 10, self.img_nave.get_width() * (self.vida / self.vida_max), 10))


class Inimigo(Nave):
    cor_mapa = {
                'vermelho': (nave_vermelha, l_vermelho),
                'azul': (nave_azul, l_azul),
                'verde': (nave_verde, l_verde)
                }

    def __init__(self, x, y, cor, vida=100):
        super().__init__(x, y, vida)
        self.img_nave, self.laser_img = self.cor_mapa[cor]
        self.mask = py.mask.from_surface(self.img_nave)

    def mover(self, vel):
        self.y += vel

    def tiro(self):
        if self.contador_cooldown == 0:
            laser = Laser(self.x-20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


def colidir(obj1, obj2):
    """
    Colidir dois objetos
    :param obj1: primeiro objeto
    :param obj2: segundo objeto
    :return: a superposição dos dois objetos
    """
    set_x = obj2.x - obj1.x
    set_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (set_x, set_y)) != None

def main():
    """
    Algoritmo principal
    :return: reinicia a janela e 'roda' o jogo
    """
    run = True
    fps = 60
    level = 0
    vidas = 5
    main_font = py.font.SysFont('comicsans', 50)
    perd_font = py.font.SysFont('comicsans', 60)
    inimigos = []
    tam_onda = 5
    vel_inimigo = 1
    vel_jogador = 5
    vel_laser = 5
    jogador = Jogador(300, 630)
    relogio = py.time.Clock()
    derrota = False
    contador_derrota = 0

    def criar_janela():
        win.blit(fundo, (0, 0))
        # draw text
        vida_tabela = main_font.render(f'Lives: {vidas}', True, (255, 255, 255))
        level_tabela = main_font.render(f'Level: {level}', True, (255, 255, 255))

        win.blit(vida_tabela, (10, 10))
        win.blit(level_tabela, (largura - level_tabela.get_width() - 10, 10))

        for inimigo in inimigos:
            inimigo.desenhar(win)

        jogador.desenhar(win)

        if derrota:
            tabela_derrota = perd_font.render('Você Perdeu!', True, (255, 255, 255))
            win.blit(tabela_derrota, (largura / 2 - tabela_derrota.get_width() / 2, 350))

        py.display.update()

    while run:
        relogio.tick(fps)
        criar_janela()

        if vidas <= 0 or jogador.vida <= 0:
            derrota = True
            contador_derrota += 1

        if derrota:
            if contador_derrota > fps * 3:
                run = False
            else:
                continue

        if len(inimigos) == 0:
            level += 1
            tam_onda += 5
            for i in range(tam_onda):
                inimigo = Inimigo(ra.randrange(50, largura - 100), ra.randrange(-1500, -100), ra.choice(['vermelho', 'verde', 'azul']))
                inimigos.append(inimigo)

        for evento in py.event.get():
            if evento.type == py.QUIT:
                quit()

        chaves = py.key.get_pressed()
        if chaves[py.K_a] and jogador.x - vel_jogador > 0:
            jogador.x -= vel_jogador
        if chaves[py.K_d] and jogador.x + vel_jogador + jogador.get_width() < largura:
            jogador.x += vel_jogador
        if chaves[py.K_w] and jogador.y - vel_jogador > 0:
            jogador.y -= vel_jogador
        if chaves[py.K_s] and jogador.y + vel_jogador + jogador.get_width() + 15 < altura:
            jogador.y += vel_jogador
        if chaves[py.K_SPACE]:
            jogador.tiro()

        for inimigo in inimigos[:]:
            inimigo.mover(vel_inimigo)
            inimigo.mover_lasers(vel_laser, jogador)

            if ra.randrange(0, 2*60) == 1:
                inimigo.tiro()

            if colidir(inimigo, jogador):
                jogador.vida -= 10
                inimigos.remove(inimigo)
            elif inimigo.y + inimigo.get_width() > altura:
                vidas -= 1
                inimigos.remove(inimigo)

        jogador.mover_lasers(-vel_laser, inimigos)


def main_menu():
    """
    Mostra o menu principal
    :return: o menu do jogo
    """
    fonte_titulo = py.font.SysFont('comicsans', 70)
    run = True
    while run:
        win.blit(fundo, (0, 0))
        title_label = fonte_titulo.render('Clique com o mouse para começar...', True, (255, 255, 255))
        win.blit(title_label, (largura / 2 - title_label.get_width() / 2, 350))
        py.display.update()
        for evento in py.event.get():
            if evento.type == py.QUIT:
                run = False
            if evento.type == py.MOUSEBUTTONDOWN:
                main()
    py.quit()


main_menu()

