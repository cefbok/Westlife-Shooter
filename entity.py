import pygame
from math import sin
from os import walk
from pygame.math import Vector2

class Entities(pygame.sprite.Sprite):
    def __init__(self, pos, groups, path, collisions):
        super().__init__(groups)

        self.assets(path)
        self.frame_index = 0
        self.status = 'down'

        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center = pos)

        # float based movement
        self.pos = Vector2(self.rect.center)
        self.direction = Vector2()
        self.speed = 200

        # collisions
        self.hitbox = self.rect.inflate(-self.rect.width * 0.6, -self.rect.height / 2)
        self.collisions = collisions
        self.mask = pygame.mask.from_surface(self.image)

        # attack
        self.attacking = False

        #health
        self.health = 3 
        self.is_vurnerable = True
        self.hit_time = pygame.time.get_ticks()
    
        self.hit_sound = pygame.mixer.Sound('./sound/hit.mp3')
        self.hit_sound.set_volume(0.3)
        self.bullet_sound = pygame.mixer.Sound('./sound/bullet.wav')
        self.bullet_sound.set_volume(0.2)
        
    def blink(self):
        if not self.is_vurnerable:
            if self.wave_val():
                mask = pygame.mask.from_surface(self.image)
                white_surface = mask.to_surface()
                white_surface.set_colorkey((0,0,0))
                self.image = white_surface
    
    def wave_val(self):
        val = sin(pygame.time.get_ticks())
        if val >= 0:
            return True
        else:
            return False

    def damage(self):
        if self.is_vurnerable:
            self.health -= 1
            self.is_vurnerable = False
            self.hit_sound.play()
    
    def vulnerable_time(self):
        if not self.is_vurnerable:
            cur_time = pygame.time.get_ticks()
            if cur_time - self.hit_time > 400:
                self.is_vurnerable = True

    def check_death(self):
        if self.health <= 0:
            self.kill()

    def assets(self, path):
        self.animations = {}
        for index, folder in enumerate(walk(path)):
            if index == 0:
                for name in folder[1]:
                    self.animations[name] = []
            else:
                for file_name in sorted(folder[2], key = lambda string: int(string.split('.')[0])):
                    path = folder[0].replace('\\','/') + '/' + file_name
                    surf = pygame.image.load(path).convert_alpha()
                    key = folder[0].split('\\')[1]
                    self.animations[key].append(surf)

    def move(self, dt):
        # normalize
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        # horizontal movement
        self.pos.x += self.direction.x * self.speed * dt 
        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx = self.hitbox.centerx
        self.collision('horizontal')

        # vertical movement
        self.pos.y += self.direction.y * self.speed * dt 
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery
        self.collision('vertical')

    def collision(self, direction):
        for sprite in self.collisions.sprites():
            if sprite.hitbox.colliderect(self.hitbox):
                if direction == 'horizontal':
                    if self.direction.x > 0:
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0:
                        self.hitbox.left = sprite.hitbox.right
                    self.rect.centerx = self.hitbox.centerx
                    self.pos.x = self.hitbox.centerx
                else: # vertical
                    if self.direction.y > 0:
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0:
                        self.hitbox.top = sprite.hitbox.bottom
                    self.rect.centery = self.hitbox.centery
                    self.pos.y = self.hitbox.centery