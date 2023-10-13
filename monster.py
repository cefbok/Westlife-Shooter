import pygame
from pygame.math import Vector2
from entity import Entities

class Monster():
    def player_distance_direction(self):
        enemy_pos = Vector2(self.rect.center)
        player_pos = Vector2(self.player.rect.center)
        distance = (player_pos - enemy_pos).magnitude()
        if distance != 0:
            direction = (player_pos - enemy_pos).normalize()
        else:
            direction = Vector2()

        return(distance, direction)

    def face_player(self):
        distance, direction = self.player_distance_direction()
        if distance < self.radius:
            if -0.5 < direction.y < 0.5:
                if direction.x < 0: # player on left
                    self.status = 'left_idle'
                elif direction.x > 0:
                    self.status = 'right_idle'
            else:
                if direction.y < 0:
                    self.status = 'up_idle'
                elif direction.y > 0:
                    self.status = 'down_idle'

    def approach_player(self):
        distance, direction = self.player_distance_direction()
        if self.attack_radius < distance < self.walk_radius:
            self.direction = direction
            self.status = self.status.split('_')[0]
        else:
            self.direction = Vector2()


class Coffin(Entities, Monster):
    def __init__(self, pos, groups, path, collisions, player):
        super().__init__(pos, groups, path, collisions)

        self.speed = 150

        # player interaction
        self.player = player
        self.radius = 550 # noticing the player
        self.walk_radius = 450 # walking toward the player
        self.attack_radius = 80 # attacking the player
    
    def attack(self):
        distance = self.player_distance_direction()[0]
        if distance < self.attack_radius and not self.attacking:
            self.attacking = True
            self.frame_index = 0

        if self.attacking:
            self.status = self.status.split('_')[0] + '_attack'
    
    def animate(self, dt):
        current_animation = self.animations[self.status]
        
        if int(self.frame_index) == 4 and self.attacking:
            if self.player_distance_direction()[0] < self.attack_radius:
                self.player.damage()


        self.frame_index += 10 * dt
        if self.frame_index >= len(current_animation):
            self.frame_index = 0 
            if self.attacking:
                self.attacking = False
           

        self.image = current_animation[int(self.frame_index)]
        self.mask = pygame.mask.from_surface(self.image)
    
    def update(self, dt):
        self.face_player()
        self.approach_player()
        self.attack()
        self.move(dt)
        self.animate(dt)
        self.blink()

        self.check_death()
        self.vulnerable_time()

        


class Cactus(Entities, Monster):
    def __init__(self, pos, groups, path, collisions, player, create_bullet):
        super().__init__(pos, groups, path, collisions)
        self.player = player
        self.radius = 600 # noticing the player
        self.walk_radius = 500 # walking toward the player
        self.attack_radius = 300 # attacking the player
        self.speed = 90

        self.create_bullet = create_bullet
        self.bullet_shot = False

    def attack(self):
        distance = self.player_distance_direction()[0]
        if distance < self.attack_radius and not self.attacking:
            self.attacking = True
            self.frame_index = 0
            self.bullet_shot = False

        if self.attacking:
            self.status = self.status.split('_')[0] + '_attack'
    
    def animate(self, dt):
        current_animation = self.animations[self.status]
        
        if int(self.frame_index) == 6 and self.attacking and not self.bullet_shot:
            direction = self.player_distance_direction()[1]
            pos = self.rect.center + direction * 150
            self.create_bullet(pos, direction)
            self.bullet_shot = True
            self.bullet_sound.play()

        self.frame_index += 10 * dt
        if self.frame_index >= len(current_animation):
            self.frame_index = 0
            if self.attacking:
                self.attacking = False
        
        self.image = current_animation[int(self.frame_index)]
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt):
        self.face_player()
        self.approach_player()
        self.attack()
        self.move(dt)
        self.animate(dt)

        self.blink()
        self.check_death()
        self.vulnerable_time()
        
        