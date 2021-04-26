# Pygame template - шаблон для создания проектов
import pygame
import random

from settings import *
from sprites import *
from os import path


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE_GAME)
        self.clock = pygame.time.Clock()
        self.running = True
        self.font_name = pygame.font.match_font(FONT_NAME)
        self.score = 0
        self.load_data()

    def load_data(self):
        self.dir = path.dirname(__file__)
        img_dir = path.join(self.dir, 'img')
        with open(path.join(self.dir, HS_FILE), 'r') as f:
            try:
                self.highscore = int(f.read())
            except:
                self.highscore = 0
        self.spritesheet = Spritesheet(path.join(img_dir, SPRITESHEET))
        self.cloud_images = []
        for i in range(1, 4):
            self.cloud_images.append(pygame.image.load(path.join(img_dir, f"cloud{i}.png")).convert())
        self.snd_dir = path.join(self.dir, "snd")
        self.jump_sound = pygame.mixer.Sound(path.join(self.snd_dir, "Jump33.wav"))
        self.boost_sound = pygame.mixer.Sound(path.join(self.snd_dir, "Boost16.wav"))

    def new(self):
        self.score = 0
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.clouds = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.mobs = pygame.sprite.Group()
        self.player = Player(self)
        for plat in PLATFORM_LIST:
            p = Platform(self, *plat)
        self.mob_timer = 0
        pygame.mixer.music.load(path.join(self.snd_dir, "Happy Tune.ogg"))
        for i in range(8):
            c = Cloud(self)
            c.rect. y += 500

        self.run()

    def run(self):
        pygame.mixer.music.play(loops=-1)
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()
        pygame.mixer.music.fadeout(500)

    def update(self):
        self.all_sprites.update()

        # создание мобов
        now = pygame.time.get_ticks()
        if now - self.mob_timer > 5000 + random.choice([-1000, -500, 0, 500, 1000]):
            self.mob_timer = now
            Mob(self)

        # столкновение с мобами
        mob_hits = pygame.sprite.spritecollide(self.player, self.mobs, False, pygame.sprite.collide_mask)
        if mob_hits:
            self.playing = False

        if self.player.vel.y > 0:
            hits = pygame.sprite.spritecollide(self.player, self.platforms, False)
            if hits:
                lowest = hits[0]
                for hit in hits:
                    if hit.rect.bottom > lowest.rect.bottom:
                        lowest = hit
                if self.player.pos.x < lowest.rect.right + 10 and \
                        self.player.pos.x > lowest.rect.left - 10:
                    if self.player.pos.y < lowest.rect.bottom:
                        self.player.pos.y = lowest.rect.top
                        self.player.vel.y = 1
                        self.player.jumping = False

        # если игрок достиг 1/4 экрана
        if self.player.rect.top <= HEIGHT / 4:
            if random.randrange(100) < 5:
                Cloud(self)
            self.player.pos.y += max(abs(self.player.vel.y), 2)
            for mob in self.mobs:
                mob.rect.y += max(abs(self.player.vel.y), 2)
            for cloud in self.clouds:
                cloud.rect.y += max(abs(self.player.vel.y // 2), 2)
            for plat in self.platforms:
                plat.rect.y += max(abs(self.player.vel.y), 2)
                if plat.rect.top > HEIGHT:
                    plat.kill()
                    self.score += 1

        # если взял бонус
        pow_hits = pygame.sprite.spritecollide(self.player, self.powerups, True)
        for pow in pow_hits:
            if pow.type == "boost":
                self.boost_sound.play()
                self.player.vel.y = -BOOST_POWER
                self.player.jumping = False

        # игрок упал вниз
        if self.player.rect.bottom > HEIGHT:
            self.playing = False

        # генерация новых платформ
        while len(self.platforms) < 6:
            width = random.randint(50, 100)
            Platform(self, random.randrange(0, WIDTH - width),
                         random.randrange(-75, -30))
            #self.all_sprites.add(p)
            #self.platforms.add(p)

    def events(self):
        for event in pygame.event.get():
            # проверка закрытия игрового окна
            if event.type == pygame.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.player.jump()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    self.player.jump_cut()

    def show_start_screen(self):
        # game splash/start screen
        pygame.mixer.music.load(path.join(self.snd_dir, 'Yippee.ogg'))
        pygame.mixer.music.play(loops=-1)
        self.screen.fill(BGCOLOR)
        self.draw_text(TITLE_GAME, 48, WHITE, WIDTH / 2, HEIGHT / 4)
        self.draw_text("Стрелки - лево, право, Пробел - прыжок", 22, WHITE, WIDTH / 2, HEIGHT / 2)
        self.draw_text("Нажмите любую клавишу для начала", 22, WHITE, WIDTH / 2, HEIGHT * 3 / 4)
        self.draw_text("Рекорд: " + str(self.highscore), 22, WHITE, WIDTH / 2, 15)
        pygame.display.flip()
        self.wait_for_key()
        pygame.mixer.music.fadeout(500)

    def show_go_screen(self):
        # game over/continue
        pygame.mixer.music.load(path.join(self.snd_dir, 'Yippee.ogg'))
        pygame.mixer.music.play(loops=-1)
        if not self.running:
            return
        self.screen.fill(BGCOLOR)
        self.draw_text("GAME OVER", 48, WHITE, WIDTH / 2, HEIGHT / 4)
        self.draw_text("Очки: " + str(self.score), 22, WHITE, WIDTH / 2, HEIGHT / 2)
        self.draw_text("Нажмите любую клавишу для начала", 22, WHITE, WIDTH / 2, HEIGHT * 3 / 4)
        if self.score > self.highscore:
            self.highscore = self.score
            self.draw_text("Новый рекорд!", 22, WHITE, WIDTH / 2, HEIGHT / 2 + 40)
            with open(path.join(self.dir, HS_FILE), 'w') as f:
                f.write(str(self.score))
        else:
            self.draw_text("Рекорд: " + str(self.highscore), 22, WHITE, WIDTH / 2,
                           HEIGHT / 2 + 40)
        pygame.display.flip()
        self.wait_for_key()
        pygame.mixer.music.fadeout(500)

    def draw(self):
        self.screen.fill(BGCOLOR)
        self.all_sprites.draw(self.screen)
        # self.screen.blit(self.player.image, self.player.rect)
        self.draw_text(str(self.score), 25, WHITE, WIDTH / 2, 15)
        pygame.display.flip()

    def wait_for_key(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pygame.KEYUP:
                    waiting = False

    def draw_text(self, text, size, color, x, y):
        font = pygame.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)


g = Game()
g.show_start_screen()
while g.running:
    g.new()
    g.show_go_screen()

pygame.quit()  # завершаем работу с pygame
