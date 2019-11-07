#!/usr/bin/python3
"""Asteroids game developer by Mike Sosa
    all sprites come from opengameart.com"""

import pygame
import random
from os import path

# GLOBAL VARIABLES ------------------------------------------------------------
WIDTH = 480
HEIGHT = 600
FPS = 60

# COLORS ----------------------------------------------------------------------
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# INIT ------------------------------------------------------------------------
pygame.init()
pygame.mixer.init(22100, -16, 2, 64)  # decraising latency on mixer
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shoot them!")
clock = pygame.time.Clock()
game_folder = path.dirname(__file__)
img_folder = path.join(game_folder, "img")
snd_folder = path.join(game_folder, "sound")
font_name = pygame.font.match_font("arial") # it will find any font similar to arial

# IMAGES ----------------------------------------------------------------------
ship_img = pygame.image.load(path.join(img_folder, "ship.png")).convert()
bullet_img = pygame.image.load(path.join(img_folder, "rocket.png")).convert()
meteor_images = []
meteor_list = ["meteor1.png", "meteor2.png", "meteor3.png", "meteor4.png",
               "meteor5.png", "meteor6.png", "meteor7.png", "meteor8.png",
               "meteor9.png"]
for img in meteor_list:
    meteor_images.append(pygame.image.load(path.join(img_folder, img)))

explosion_anim = {}
explosion_anim['lg'] = []
explosion_anim['sm'] = []
for i in range(1, 9):
    filename = 'explosion{}.png'.format(i)
    img = pygame.image.load(path.join(img_folder, filename)).convert()
    img_lg = pygame.transform.scale(img, (75, 75))
    explosion_anim['lg'].append(img_lg)
    img_sm = pygame.transform.scale(img, (35, 35))
    explosion_anim['sm'].append(img_sm)

# SOUNDS ----------------------------------------------------------------------
shoot_sound = pygame.mixer.Sound(path.join(snd_folder, 'laser.wav'))
double_shoot_sound = pygame.mixer.Sound(path.join(snd_folder, 'shoot2.wav'))
energy_sound = pygame.mixer.Sound(path.join(snd_folder, 'energy.wav'))
double_ready = pygame.mixer.Sound(path.join(snd_folder, 'armed.wav'))
killed_sound = pygame.mixer.Sound(path.join(snd_folder, 'killed.wav'))
pygame.mixer.music.load(path.join(snd_folder, "FoxSynergy.mp3"))
pygame.mixer.music.set_volume(0.4)
exp_soundBig=pygame.mixer.Sound(path.join(snd_folder, 'explosion1.wav'))
exp_soundSmall=pygame.mixer.Sound(path.join(snd_folder, 'explosion2.wav'))


# CLASSES ---------------------------------------------------------------------
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(path.join(img_folder, "ship.png"))
        self.image = pygame.transform.scale(self.image, (80, 70))
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0
        self.shield = 100
        self.guns = 1

    def update(self):
        self.speedx = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speedx =- 5
        if keystate[pygame.K_RIGHT]:
            self.speedx = 5
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        self.rect.x += self.speedx

    def shoot(self):
        bullet=Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)
        shoot_sound.play()

    def shoot2(self):
        bullet1 = Bullet(self.rect.centerx - 20, self.rect.top)
        bullet2 = Bullet(self.rect.centerx + 20, self.rect.top)
        all_sprites.add(bullet1, bullet2)
        bullets.add(bullet1, bullet2    )
        double_shoot_sound.play()

class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(meteor_images)
        self.image = self.image_orig.copy()
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1, 8)
        self.speedx = random.randrange(-2, 2)
        self.rot = 0
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()  # to get the time
        self.radius = int(self.rect.width * .85 / 2)

    def rotate(self):
        """Rotates the meteorits"""
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:  # if greather thatn 50 mil update
            self.last_update=now
            # make sure it will only rotate up to 360
            self.rot = (self.rot + self.rot_speed) % 360
            new_image = pygame.transform.rotate(self.image_orig, self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def update(self):
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT + 10 or self.rect.left < -80 or self.rect.right > WIDTH + 80:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 8)
            self.speedx = random.randrange(-2, 2)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(path.join(img_folder, "laser2.png")).convert()
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

class Explosion(pygame.sprite.Sprite):

    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update >  self.frame_rate:
            self.last_update = now
            self.frame += 1
        if self.frame == len(explosion_anim[self.size]):
            self.kill()
        else:
            center = self.rect.center
            self.image = explosion_anim[self.size][self.frame]
            self.image.set_colorkey(BLACK)
            self.rect = self.image.get_rect()
            self.rect.center = center

class Energy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(path.join(img_folder, "energy.png")).convert()
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = 5

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom > HEIGHT:
            self.kill()

# FUNCTIONS ------------------------------------------------------------------
def newMob():
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)

def draw_shield_bar(surface, x, y, value):
    if value <= 0:
        value = 0
    BAR_HEIGHT = 10
    BAR_WIDTH = 100
    fill = (value / 100) * BAR_WIDTH # So we can always have a percentage
    border_rect = pygame.Rect(x, y, BAR_WIDTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    if value > 40:
        pygame.draw.rect(surface, GREEN, fill_rect)
    else:
        pygame.draw.rect(surface, RED, fill_rect)
    pygame.draw.rect(surface, WHITE, border_rect, 1)

def draw_text(surface, text, f_size, x, y):
    font = pygame.font.Font(font_name, f_size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surface.blit(text_surface, text_rect)

# CREATING SPRiTES ------------------------------------------------------------
all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()
mobs = pygame.sprite.Group()
energys = pygame.sprite.Group()
player = Player()
all_sprites.add(player)

for i in range(6):
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)

score = 0 # score on the screen
pygame.mixer.music.play(loops =- 1) # to repeat the bg when finished

# GAME LOOP -------------------------------------------------------------------
running = True
while running:
    # Keep clock running at right speed
    clock.tick(FPS)
    # Process input
    for event in pygame.event.get():
        # Chading closing window
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if player.guns == 1:
                    player.shoot()
                else:
                    player.shoot2()

    # If bullet hits a mob
    hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
    for hit in hits:
        score += 50 - hit.radius
        expLg = Explosion(hit.rect.center, 'lg')
        expSm = Explosion(hit.rect.center, 'sm')
        if m.rect.width > 100:
            exp_soundBig.play()
            all_sprites.add(expLg)
        else:
            exp_soundSmall.play()
            all_sprites.add(expSm)
        newMob()
        if hit.radius == 6:
            energy = Energy(hit.rect.x, hit.rect.y)
            all_sprites.add(energy)
            energys.add(energy)

    # If mob hits player
    hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)
    for hit in hits:
        player.shield -= hit.radius * 2
        player.guns = 1
        if player.shield <= 0:
            running = False
        expSm = Explosion(hit.rect.center, 'sm')
        all_sprites.add(expSm)
        killed_sound.play()
        newMob()

    # IF energy hits player
    hits = pygame.sprite.spritecollide(player, energys, True, pygame.sprite.collide_circle)
    if hits:
        if player.shield <= 100:
            if player.shield + 10 > 100:
                player.shield = 100
                player.guns = 2
                energy_sound.play()
            else:
                player.shield += 10
                player.guns = 1
                energy_sound.play()

    # Update
    all_sprites.update()
    # Draw - Render
    screen.fill(BLACK)
    all_sprites.draw(screen)
    draw_shield_bar(screen, 10, 10, player.shield) # surface, position and value to draw
    draw_text(screen, str(score), 20, WIDTH - 30, 10) # surface, text, fontsize, x, y
    # After drwaing everything flip the display
    pygame.display.flip()