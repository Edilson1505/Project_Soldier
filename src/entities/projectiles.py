import pygame
import math
import random
from ..core.settings import DISPLAY_SIZE, SCALE, ANIM_SPEED

class Bullet:
    def __init__(self, x, y, right=True):
        self.x, self.y = x, y 
        self.speed = 18.0 * (1 if right else -1) 
        self.alive = True 
        self.life_timer = 120
        
    def update(self, obstacles):
        self.x += self.speed 
        self.life_timer -= 1 
        hitbox = pygame.Rect(self.x-5, self.y-5, 10, 10)
        if any(hitbox.colliderect(ob) for ob in obstacles) or self.life_timer <= 0: 
            self.alive = False
            
    def draw(self, surface, cam):
        sx, sy = cam.apply(self.x, self.y)
        pygame.draw.circle(surface, (255, 230, 150), (sx, sy), 4)
        pygame.draw.circle(surface, (255, 255, 255), (sx, sy), 2)

class GrenadeProjectile:
    def __init__(self, x, y, right, explosion_anim):
        self.x, self.y = x, y 
        self.vx = 12.0 * (1 if right else -1) 
        self.vy = -8.0
        self.grav = 0.5 
        self.life = 60 
        self.alive = True 
        self.has_exploded = False
        
    def update(self, obstacles):
        self.x += self.vx 
        self.y += self.vy 
        self.vy += self.grav 
        self.life -= 1
        if self.life <= 0: 
            self.has_exploded = True 
            self.alive = False
            
    def draw(self, surface, cam):
        sx, sy = cam.apply(self.x, self.y)
        pygame.draw.circle(surface, (50, 120, 50), (sx, sy), 6)
        pygame.draw.rect(surface, (150, 200, 150), (sx-2, sy-2, 4, 4)) 

class ExplosionEffect:
    def __init__(self, x, y, anim):
        self.x, self.y = x, y 
        self.anim = anim 
        self.frame = 0 
        self.timer = 0 
        self.alive = True
        
    def update(self, _):
        self.timer += 1
        speed = ANIM_SPEED.get("Explosion", 3)
        if self.timer >= speed:
            self.timer = 0 
            self.frame += 1
            if self.frame >= len(self.anim): 
                self.alive = False
                
    def draw(self, surface, cam):
        if self.frame < len(self.anim):
            sx, sy = cam.apply(self.x, self.y)
            f = self.anim[self.frame]
            fr = f.get_rect()
            # Center the explosion on the impact point
            fr.center = (sx, sy)
            surface.blit(f, fr.topleft)
