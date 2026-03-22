import pygame
import math
import random
from .settings import (DISPLAY_SIZE, SPEED, ANIM_FRAMES, ANIM_SPEED, SCALE, ROOMS_MAP, ROOM_W, ROOM_H)

class EnemySoldier:
    def __init__(self, x, y, anims):
        self.x, self.y = float(x), float(y)
        self.vx, self.vy = 0.0, 0.0
        self.anims = anims
        self.current_anim = "Idle"
        self.frame_index = 0 ; self.frame_timer = 0
        self.facing_right = True
        self.health = 50
        self.alive = True
        
        # Nombres en Clave Tácticos
        apodos = ["Sargento Rojo", "Cabo Fenix", "Soldado Sombra", "Agente Vaga", "Elite Bravo", "Infiltrado"]
        self.name = random.choice(apodos)
        
        # Hitbox refinada (más pequeña para mejores colisiones)
        self.hit_w, self.hit_h = 20 * SCALE, 8 * SCALE
        self.detect_range = 650
        self.attack_range = 280
        self.shoot_cooldown = random.randint(30, 90)
        self.bullets = []
        self.f_name = pygame.font.SysFont("Consolas", 14, bold=True)

    def update(self, player_x, player_y, obstacles):
        if not self.alive: return
        
        dist = math.hypot(player_x - self.x, player_y - self.y)
        self.vx, self.vy = 0.0, 0.0
        
        if dist < self.detect_range:
            angle = math.atan2(player_y - self.y, player_x - self.x)
            self.facing_right = player_x > self.x
            
            if dist > self.attack_range - 40:
                self.vx, self.vy = math.cos(angle) * SPEED * 0.7, math.sin(angle) * SPEED * 0.7
            
            if dist < self.attack_range:
                if self.shoot_cooldown <= 0:
                    self._shoot()
                    self.shoot_cooldown = 70
        
        if self.shoot_cooldown > 0: self.shoot_cooldown -= 1
        
        # 🛡️ COLISIONES CON OBSTÁCULOS (Paredes)
        new_x = self.x + self.vx
        rx = pygame.Rect(new_x + (DISPLAY_SIZE - self.hit_w)//2, self.y + DISPLAY_SIZE - self.hit_h - 22, self.hit_w, self.hit_h)
        if not any(rx.colliderect(obs) for obs in obstacles): self.x = new_x
        
        new_y = self.y + self.vy
        ry = pygame.Rect(self.x + (DISPLAY_SIZE - self.hit_w)//2, new_y + DISPLAY_SIZE - self.hit_h - 22, self.hit_w, self.hit_h)
        if not any(ry.colliderect(obs) for obs in obstacles): self.y = new_y
        
        # 🎞️ ANIMACIÓN
        if self.shoot_cooldown > 45: self.set_animation("Shot_2")
        elif abs(self.vx) > 0.1 or abs(self.vy) > 0.1: self.set_animation("Walk")
        else: self.set_animation("Idle")
            
        self.frame_timer += 1
        if self.frame_timer >= ANIM_SPEED.get(self.current_anim, 5):
            self.frame_timer = 0 ; self.frame_index = (self.frame_index + 1) % len(self.anims[self.current_anim])

    def _shoot(self):
        from .projectiles import Bullet
        bx = self.x + (DISPLAY_SIZE // 2) + (38 * SCALE if self.facing_right else -38 * SCALE)
        by = self.y + (DISPLAY_SIZE // 2) + 13 * SCALE
        self.bullets.append(Bullet(bx, by, self.facing_right))

    def take_damage(self, amt):
        self.health -= amt
        if self.health <= 0: self.alive = False

    def set_animation(self, name):
        if name != self.current_anim:
            self.current_anim = name ; self.frame_index = 0 ; self.frame_timer = 0

    def draw(self, surface, cam):
        if not self.alive: return
        sx, sy = cam.apply(self.x, self.y)
        
        # Nombre y Barra de Vida
        n_txt = self.f_name.render(self.name, True, (255, 100, 100))
        surface.blit(n_txt, (sx + (DISPLAY_SIZE//2) - n_txt.get_width()//2, sy - 25))
        pygame.draw.rect(surface, (50, 0, 0), (sx + 20, sy - 8, 80, 5))
        pygame.draw.rect(surface, (255, 50, 50), (sx + 20, sy - 8, int(80 * (self.health/50)), 5))
        
        frame = self.anims[self.current_anim][self.frame_index]
        if not self.facing_right: frame = pygame.transform.flip(frame, True, False)
        enemy_frame = frame.copy()
        enemy_frame.fill((255, 150, 150, 255), special_flags=pygame.BLEND_RGBA_MULT)
        surface.blit(enemy_frame, (sx, sy))
