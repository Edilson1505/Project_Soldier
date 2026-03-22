import pygame
import math
import random
from .settings import (BULLET_SPEED, BULLET_SIZE, SCALE, ANIM_SPEED)

class Bullet:
    def __init__(self, x, y, facing_right):
        self.x, self.y = x, y
        self.vx = BULLET_SPEED if facing_right else -BULLET_SPEED
        self.alive = True
        self.size = BULLET_SIZE * SCALE

    def update(self, walls):
        self.x += self.vx
        rect = pygame.Rect(self.x - self.size//2, self.y - self.size//2, self.size, self.size)
        if any(rect.colliderect(w) for w in walls): self.alive = False
        if abs(self.x) > 10000: self.alive = False

    def draw(self, surface, cam):
        sx, sy = cam.apply(self.x, self.y)
        pygame.draw.circle(surface, (255, 255, 180), (int(sx), int(sy)), int(self.size//2))
        pygame.draw.circle(surface, (255, 255, 255), (int(sx), int(sy)), int(self.size//4))

class ExplosionEffect:
    def __init__(self, x, y, frames):
        self.x, self.y = x, y
        self.frames = frames
        self.frame_index = 0 ; self.timer = 0 ; self.alive = True

    def update(self, walls=None):
        if not self.alive: return
        self.timer += 1
        if self.timer >= ANIM_SPEED["Explosion"]:
            self.timer = 0 ; self.frame_index += 1
            if self.frame_index >= len(self.frames): self.alive = False

    def draw(self, surface, cam):
        if not self.alive or self.frame_index >= len(self.frames): return
        sx, sy = cam.apply(self.x, self.y)
        f = self.frames[self.frame_index]
        w, h = f.get_size()
        surface.blit(f, (sx - w//2, sy - h//2))

class GrenadeProjectile:
    """Granada con eje Z simulado para evitar que caiga al fondo de la pantalla."""
    def __init__(self, x, y, facing_right, explosion_frames):
        self.x, self.y = x, y # Posición en el plano del suelo
        self.z = 0.0          # Altura simulada
        self.vz = -15.0       # Velocidad de salto inicial (negativo es arriba)
        self.vx = 8 if facing_right else -8
        self.vy = random.uniform(-2, 2) # Pequeña desviación aleatoria en Y
        
        self.gravity = 0.7
        self.alive = True
        self.has_exploded = False
        self.explosion_frames = explosion_frames
        self.angle = 0 ; self.rot_speed = random.uniform(10, 20) * (1 if facing_right else -1)

    def update(self, walls):
        if self.has_exploded: return
        
        # Movimiento en el Plano (Suelo)
        self.x += self.vx
        self.y += self.vy
        
        # Movimiento en el Eje Z (Altura)
        self.vz += self.gravity
        self.z += self.vz
        
        # Detección de Colisión con Muros (Plano X,Y)
        rect = pygame.Rect(self.x - 10, self.y - 10, 20, 20)
        for w in walls:
            if rect.colliderect(w):
                self.explode()
                return

        # IMPACTO EN EL SUELO (Cuando la altura vuelve a 0 o más)
        if self.z >= 0:
            self.z = 0 # Asegurar que explote en el suelo
            self.explode()

    def explode(self):
        self.has_exploded = True
        self.alive = False

    def draw(self, surface, cam):
        if self.has_exploded: return
        # Aplicamos la altura Z a la posición de dibujado Y
        sx, sy = cam.apply(self.x, self.y + self.z)
        self.angle += self.rot_speed
        
        # Sombra en el suelo (opcional pero ayuda a la profundidad)
        shadow_sx, shadow_sy = cam.apply(self.x, self.y)
        pygame.draw.ellipse(surface, (0, 0, 0, 100), (shadow_sx-12, shadow_sy-6, 24, 12))
        
        # Cuerpo de la granada
        pygame.draw.circle(surface, (40, 60, 30), (int(sx), int(sy)), 9)
        pygame.draw.circle(surface, (180, 220, 150), (int(sx), int(sy)), 9, 2)
        # Detalle de mecha
        ex = sx + math.cos(math.radians(self.angle)) * 7
        ey = sy + math.sin(math.radians(self.angle)) * 7
        pygame.draw.line(surface, (255, 255, 255), (sx, sy), (ex, ey), 2)
