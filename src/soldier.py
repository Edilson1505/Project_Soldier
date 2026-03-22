import pygame
from .settings import (DISPLAY_SIZE, SPEED, WORLD_W, WORLD_H, ANIM_FRAMES, ANIM_SPEED, SCALE, MAX_AMMO, MAX_GRENADES)
from .utils import load_spritesheet
from .projectiles import Bullet, GrenadeProjectile, ExplosionEffect

class Soldier:
    def __init__(self, x: float, y: float):
        self.x, self.y = float(x), float(y)
        self.vx = 0.0 ; self.vy = 0.0
        self.facing_right = True
        
        self.anims = {anim: load_spritesheet(anim, fc) for anim, fc in ANIM_FRAMES.items()}
        if "Explosion" in self.anims:
            self.anims["Explosion"] = self.anims["Explosion"][-5:]
        
        self.current_anim = "Idle"
        self.frame_index = 0 ; self.frame_timer = 0
        self.ammo = MAX_AMMO ; self.grenades = MAX_GRENADES
        self.is_shooting = False ; self.is_reloading = False ; self.is_throwing = False
        self.wants_to_shoot_auto = False ; self.action_spawned = False 
        self.bullets = [] ; self.projectiles = []
        
        self.hit_w = 25 * SCALE ; self.hit_h = 10 * SCALE

    def shoot(self, active=True):
        if self.is_reloading or self.is_throwing: self.wants_to_shoot_auto = False; return
        if self.ammo <= 0: active = False
        self.wants_to_shoot_auto = active
        if active and not self.is_shooting: self._start_new_shot()

    def reload(self):
        if not self.is_reloading and not self.is_throwing and self.ammo < MAX_AMMO:
            self.is_reloading = True; self.is_shooting = False; self.wants_to_shoot_auto = False
            self.set_animation("Recharge")

    def throw_grenade(self):
        if not self.is_throwing and self.grenades > 0:
            self.is_throwing = True; self.is_shooting = False; self.is_reloading = False
            self.wants_to_shoot_auto = False; self.action_spawned = False 
            self.set_animation("Grenade")

    def _start_new_shot(self):
        self.is_shooting = True ; self.set_animation("Shot_2") ; self.action_spawned = False

    def set_animation(self, name: str):
        if name != self.current_anim:
            self.current_anim = name ; self.frame_index = 0 ; self.frame_timer = 0

    def update(self, keys, obstacles: list):
        for b in self.bullets[:]:
            b.update(obstacles)
            if not b.alive: self.bullets.remove(b)
        for g in self.projectiles[:]:
            g.update(obstacles)
            if isinstance(g, GrenadeProjectile) and g.has_exploded:
                self.projectiles.remove(g)
                self.projectiles.append(ExplosionEffect(g.x, g.y, self.anims["Explosion"]))
            elif not g.alive: self.projectiles.remove(g)

        # MOVIMIENTO (Permitido incluso al disparar)
        run = (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and not self.is_reloading
        cur_spd = SPEED * 0.6 if self.is_reloading else SPEED * (1.8 if run else 1.0)
        vx, vy = 0.0, 0.0
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: vx = -cur_spd; self.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: vx =  cur_spd; self.facing_right = True
        if keys[pygame.K_UP]    or keys[pygame.K_w]: vy = -cur_spd
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]: vy =  cur_spd
        if vx != 0 and vy != 0: vx *= 0.7071 ; vy *= 0.7071

        nx = self.x + vx
        rx = pygame.Rect(nx + (DISPLAY_SIZE - self.hit_w)//2, self.y + DISPLAY_SIZE - self.hit_h - 22, self.hit_w, self.hit_h)
        if not any(rx.colliderect(obs) for obs in obstacles): self.x = nx
        ny = self.y + vy
        ry = pygame.Rect(self.x + (DISPLAY_SIZE - self.hit_w)//2, ny + DISPLAY_SIZE - self.hit_h - 22, self.hit_w, self.hit_h)
        if not any(ry.colliderect(obs) for obs in obstacles): self.y = ny

        # Prioridad de Animación: Granada > Recarga > Disparo > Movimiento > Idle
        if self.is_throwing: pass # Sigue con Grenade
        elif self.is_reloading: self.set_animation("Recharge")
        elif self.is_shooting and (vx == 0 and vy == 0): self.set_animation("Shot_2")
        else:
            mv = vx != 0 or vy != 0
            self.set_animation("Run" if (run and mv) else "Walk" if mv else "Idle")

        self.frame_timer += 1
        if self.frame_timer >= ANIM_SPEED[self.current_anim]:
            self.frame_timer = 0; self.frame_index += 1
            if not self.action_spawned:
                if self.is_shooting and self.frame_index == 1:
                    bx = self.x + (DISPLAY_SIZE // 2) + (38 * SCALE if self.facing_right else -38 * SCALE)
                    by = self.y + (DISPLAY_SIZE // 2) + 13 * SCALE
                    self.bullets.append(Bullet(bx, by, self.facing_right))
                    self.ammo -= 1; self.action_spawned = True
                elif self.is_throwing and self.frame_index == 6:
                    gx, gy = self.x + (DISPLAY_SIZE // 2), self.y + (DISPLAY_SIZE // 2) - 15 * SCALE
                    self.projectiles.append(GrenadeProjectile(gx, gy, self.facing_right, self.anims["Explosion"]))
                    self.grenades -= 1 ; self.action_spawned = True
            if self.frame_index >= len(self.anims[self.current_anim]):
                self.frame_index = 0
                if self.is_reloading: self.is_reloading = False; self.ammo = MAX_AMMO; self.set_animation("Idle")
                elif self.is_throwing: self.is_throwing = False; self.set_animation("Idle")
                elif self.is_shooting:
                    if self.wants_to_shoot_auto and self.ammo > 0: self._start_new_shot()
                    else: self.is_shooting = False; self.set_animation("Idle")

    def draw(self, surface: pygame.Surface, cam):
        sx, sy = cam.apply(self.x, self.y)
        # 🌑 SOMBRA BAJADA Y CENTRADA (sy + DISPLAY_SIZE - 4)
        sh_x, sh_y = sx + (DISPLAY_SIZE // 2) - 10, sy + DISPLAY_SIZE - 4
        pygame.draw.ellipse(surface, (0, 0, 0, 65), (sh_x - 50, sh_y - 12, 100, 24))
        
        for b in self.bullets: b.draw(surface, cam)
        for g in self.projectiles: g.draw(surface, cam)
        frame = self.anims[self.current_anim][self.frame_index]
        if not self.facing_right: frame = pygame.transform.flip(frame, True, False)
        surface.blit(frame, (sx, sy))
