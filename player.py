import pygame, sys
from pygame.math import Vector2
from entity import Entities

class Player(Entities):
    def __init__(self, pos, groups, path, collisions, create_bullet):
        super().__init__(pos, groups, path, collisions)
        self.create_bullet = create_bullet
        self.bullet_shot = False

    def input(self):
        keys = pygame.key.get_pressed()
        
        if not self.attacking:
            if keys[pygame.K_UP]:
                self.status = 'up'
                self.direction.y = -1
            elif keys[pygame.K_DOWN]:
                self.status = 'down'
                self.direction.y = 1
            else:
                self.direction.y = 0

            if keys[pygame.K_RIGHT]:
                self.status = 'right'
                self.direction.x = 1
            elif keys[pygame.K_LEFT]:
                self.status = 'left'
                self.direction.x = -1
            else:
                self.direction.x = 0
            
            if keys[pygame.K_SPACE]:
                self.attacking = True
                self.direction = Vector2()
                self.frame_index = 0
                self.bullet_shot = False

                match self.status.split('_')[0]:
                    case 'left': self.bullet_direction = Vector2(-1, 0)
                    case 'right': self.bullet_direction = Vector2(1, 0)
                    case 'up': self.bullet_direction = Vector2(0, -1)
                    case 'down': self.bullet_direction = Vector2(0, 1)

    def get_status(self):
        # idle
        if self.direction.x == 0 and self.direction.y == 0:
            self.status = self.status.split('_')[0] + '_idle'
            
        # attacking
        if self.attacking:
            self.status = self.status.split('_')[0] + '_attack'

    def animate(self ,dt):
        current_animation = self.animations[self.status]
        
        self.frame_index += 10 * dt

        if int(self.frame_index) == 2 and self.attacking and not self.bullet_shot:
            bullet_pos = self.rect.center + self.bullet_direction * 80
            self.create_bullet(bullet_pos, self.bullet_direction)
            self.bullet_shot = True
            self.bullet_sound.play()

        if self.frame_index >= len(current_animation):
            self.frame_index = 0
            if self.attacking:
                self.attacking = False

        self.image = current_animation[int(self.frame_index)]
        self.mask = pygame.mask.from_surface(self.image)

    def check_death(self):
        if self.health <= 0:
            pygame.quit()
            sys.exit() 

    def update(self, dt):
        self.input()
        self.get_status()
        self.move(dt)
        self.animate(dt)

        #damge
        self.blink()
        self.check_death()
        self.vulnerable_time()
        