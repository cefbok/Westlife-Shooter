import pygame, sys
from setting import *
from player import Player
from sprite import Sprite, Bullet
from pygame.math import Vector2
from pytmx.util_pygame import load_pygame
from monster import *

class AllSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.offset = Vector2()
        self.display_surface = pygame.display.get_surface()
        self.bg = pygame.image.load('./graphics/other/bg.png').convert()
    
    def custom_draw(self, player):
        self.offset.x = player.rect.centerx - window_w / 2
        self.offset.y = player.rect.centery - window_h / 2

        self.display_surface.blit(self.bg, -self.offset)
        for sprite in sorted(self.sprites(), key = lambda sprite: sprite.rect.centery):
            offset_rect = sprite.image.get_rect(center = sprite.rect.center)
            offset_rect.center -= self.offset 
            self.display_surface.blit(sprite.image, offset_rect)

class Game:
    def __init__(self):         
        pygame.init()
        pygame.display.set_caption('Western Front')
        self.clock = pygame.time.Clock()
        self.display_surface = pygame.display.set_mode((window_w, window_h))
        self.bullet_surf = pygame.image.load('./graphics/other/particle.png').convert_alpha()

        # groups
        self.all_sprites = AllSprites()
        self.obstacles = pygame.sprite.Group()
        self.bullet = pygame.sprite.Group()
        self.monsters = pygame.sprite.Group()

        self.setup()
        self.music = pygame.mixer.Sound('./sound/music.mp3')
        self.music.set_volume(0.6)
        self.music.play(loops = -1)
        

    def bullets(self, pos, direction):
        Bullet(pos, direction, self.bullet_surf, [self.all_sprites, self.bullet])

    def bullet_collision(self):

        # bullet obstacle collision
        for obstacle in self.obstacles.sprites():
            pygame.sprite.spritecollide(obstacle, self.bullet, True)

        # bullet monster collision
        for bullets in self.bullet.sprites():
            sprites = pygame.sprite.spritecollide(bullets, self.monsters, False, pygame.sprite.collide_mask)

            if sprites:
                bullets.kill()
                for sprite in sprites:
                    sprite.damage()

        if pygame.sprite.spritecollide(self.player, self.bullet, True, pygame.sprite.collide_mask):
            self.player.damage()

    def setup(self):
        tmx_map = load_pygame('./data/map.tmx')

        # tiles / fence
        for x, y, surf in tmx_map.get_layer_by_name('fence').tiles():
            Sprite((x * 64, y * 64),surf, [self.all_sprites, self.obstacles])

        # objects
        for obj in tmx_map.get_layer_by_name('Objects'):
            Sprite((obj.x, obj.y), obj.image, [self.all_sprites, self.obstacles])

        # player pos
        for obj in tmx_map.get_layer_by_name('Entities'):
            if obj.name == 'Player':
                self.player = Player(
                    pos = (obj.x, obj.y), 
                    groups = self.all_sprites, 
                    path = paths['player'], 
                    collisions = self.obstacles, 
                    create_bullet = self.bullets)
        
        # enemy !
            if obj.name == 'Coffin':
                self.coffin = Coffin(
                    (obj.x, obj.y), 
                    [self.all_sprites, self.monsters], 
                    paths['coffin'], 
                    self.obstacles, 
                    self.player)
            if obj.name == 'Cactus':
                self.coffin = Cactus(
                    (obj.x, obj.y), 
                    [self.all_sprites, self.monsters], 
                    paths['cactus'], 
                    self.obstacles, 
                    self.player,
                    self.bullets)

    def Run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            dt = self.clock.tick() / 1000

            # update
            self.all_sprites.update(dt)
            self.bullet_collision()

            # draw
            self.display_surface.fill('black')
            self.all_sprites.custom_draw(self.player)

            pygame.display.update()

if __name__ == '__main__':
    game = Game()
    game.Run()
