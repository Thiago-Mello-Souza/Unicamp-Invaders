import pygame
import os
import time
import random
from pygame import mixer
pygame.font.init()

pygame.init()

#tamanho da tela
LARGURA, ALTURA = 600, 800
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Unicamp Invaders")

#tamanho objetos
TAMANHO_INIMIGO = (90, 90)
TAMANHO_PLAYER = (70, 63)
TAMANHO_LASER = (14, 38)

#carregando imagens
BALDO = pygame.transform.scale(pygame.image.load(os.path.join("img", "professor1.png")), TAMANHO_INIMIGO)
MAIALLE = pygame.transform.scale(pygame.image.load(os.path.join("img", "professor2.png")), TAMANHO_INIMIGO)
BRITTES = pygame.transform.scale(pygame.image.load(os.path.join("img", "professor3.png")), TAMANHO_INIMIGO)
AAAKI = pygame.transform.scale(pygame.image.load(os.path.join("img", "formiga.png")), TAMANHO_PLAYER)
LASER_VERMELHO = pygame.transform.scale(pygame.image.load(os.path.join("img", "laser_vermelho.png")), TAMANHO_LASER)
LASER_VERDE = pygame.transform.scale(pygame.image.load(os.path.join("img", "laser_verde.png")), TAMANHO_LASER)
LASER_AMARELO = pygame.transform.scale(pygame.image.load(os.path.join("img", "laser_amarelo.png")), TAMANHO_LASER)
LASER_AZUL = pygame.transform.scale(pygame.image.load(os.path.join("img", "laser_azul.png")), TAMANHO_LASER)
FUNDO = pygame.transform.scale(pygame.image.load(os.path.join("img", "fundo.png")), (LARGURA, ALTURA))

#carregando sons
pygame.mixer.music.load(os.path.join("som", "background.wav"))
pygame.mixer.music.play(-1)
fogo = pygame.mixer.Sound('som/slaser.wav')
boom = pygame.mixer.Sound('som/sexplosao.wav')
boom2 = pygame.mixer.Sound('som/aaakiexp.wav')

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, altura):
        return not(self.y <= altura and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)

class Nave:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.nave_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.nave_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers[:]:
            laser.move(vel)
            if laser.off_screen(ALTURA):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def tiro(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_largura(self):
        return self.nave_img.get_width() 

    def get_altura(self):
        return self.nave_img.get_height() 

class Player(Nave):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.nave_img = AAAKI
        self.laser_img = LASER_AZUL
        self.mask = pygame.mask.from_surface(self.nave_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers[:]:
            laser.move(vel)
            if laser.off_screen(ALTURA):
                self.lasers.remove(laser)
            else:
                for obj in objs[:]:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)
                            boom.play()

    def tiro(self):
        if self.cool_down_counter == 0:
            laser_x = self.x + (self.get_largura() // 2) - (self.laser_img.get_width() // 2)
            laser = Laser(laser_x, self.y, self.laser_img)
            
            self.lasers.append(laser)
            self.cool_down_counter = 1
            fogo.play() 

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.nave_img.get_height() + 10, self.nave_img.get_width(), 10)) 
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.nave_img.get_height() + 10, self.nave_img.get_width() * (self.health / self.max_health), 10))

class Inimigo(Nave):
    COLOR_MAP = {
        "red": (BALDO, LASER_VERMELHO),
        "green": (MAIALLE, LASER_VERDE),
        "yellow": (BRITTES, LASER_AMARELO)
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.nave_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.nave_img)

    def move(self, vel):
        self.y += vel

    def tiro(self):
        if self.cool_down_counter == 0:
            laser_x = self.x + (self.get_largura() // 2) - (self.laser_img.get_width() // 2) 
            laser = Laser(laser_x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def main():
    run = True
    FPS = 60
    nivel = 0
    vidas = 3
    
    # fontes
    main_font = pygame.font.SysFont("verdana", 50)
    lost_font = pygame.font.SysFont("verdana", 65)
    win_font = pygame.font.SysFont("verdana", 45)

    inimigos = []
    wave_length = 5
    inimigo_vel = 1
    
    player_vel = 7
    laser_vel = 7

    player = Player(262, 650) 

    clock = pygame.time.Clock()

    win = False
    win_count = 0
    lost = False
    lost_count = 0

    def redraw_window():
        TELA.blit(FUNDO, (0, 0))
        vidas_label = main_font.render(f"Vidas: {vidas}", 1, (255, 255, 255))
        nivel_label = main_font.render(f"Nível: {nivel}", 1, (255, 255, 255))

        TELA.blit(vidas_label, (10, 10))
        TELA.blit(nivel_label, (LARGURA - nivel_label.get_width() - 10, 10)) 

        for inimigo in inimigos:
            inimigo.draw(TELA)

        player.draw(TELA)

        if lost:
            lost_label = lost_font.render("Reprovado!", 1, (255, 255, 255))
            TELA.blit(lost_label, (LARGURA / 2 - lost_label.get_width() / 2, ALTURA / 2)) 

        pygame.display.update()

        if win:
            win_label = win_font.render("Passou de Semestre!", 1, (255, 255, 255))
            TELA.blit(win_label, (LARGURA / 3 - win_label.get_width() / 3, ALTURA / 2))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if vidas <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if nivel > 6:
            win = True
            win_count += 1

        if win:
            if win_count > FPS * 3:
                run = False
            else:
                continue
            
        if player.health <= 0:
                    vidas -= 1
                    boom2.play()
                    player.health = 100
                    player.x = 262 
                    player.y = 650 
                    inimigos.clear() 
                    redraw_window() 
                    pygame.time.delay(1500) 

        if len(inimigos) == 0:
            nivel += 1
            wave_length += 5
            for i in range(wave_length):
                inimigo = Inimigo(random.randrange(50, LARGURA - 100), random.randrange(-1500, -100), random.choice(["red", "green", "yellow"]))
                inimigos.append(inimigo)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False 

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x - player_vel > 0:
            player.x -= player_vel
        if keys[pygame.K_RIGHT] and player.x + player_vel + player.get_largura() < LARGURA: 
            player.x += player_vel
        if keys[pygame.K_UP] and player.y - player_vel > 0:
            player.y -= player_vel
        if keys[pygame.K_DOWN] and player.y + player_vel + player.get_altura() + 15 < ALTURA:
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.tiro()

        for inimigo in inimigos[:]:
            inimigo.move(inimigo_vel)
            inimigo.move_lasers(laser_vel, player)

            if random.randrange(0, 2 * 60) == 1:
                inimigo.tiro()

            if collide(inimigo, player):
                player.health -= 10
                inimigos.remove(inimigo)
                boom2.play()
            elif inimigo.y + inimigo.get_altura() > ALTURA: 
                vidas -= 1
                inimigos.remove(inimigo)

        player.move_lasers(-laser_vel, inimigos)

def main_menu():
    title_font = pygame.font.SysFont("verdana", 40)
    run = True
    while run:
        TELA.blit(FUNDO, (0, 0))
        title_label = title_font.render("CLIQUE PARA COMEÇAR!", 1, (255, 255, 255))
        TELA.blit(title_label, (LARGURA / 2 - title_label.get_width() / 2, ALTURA / 2))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()

main_menu()