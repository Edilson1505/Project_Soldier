import pygame
import random
from src.core.settings import (DISPLAY_SIZE, SPEED, ANIM_FRAMES, ANIM_SPEED, SCALE, MAX_AMMO, MAX_GRENADES)
from src.core.utils import load_spritesheet
from src.entities.projectiles import Bullet, GrenadeProjectile, ExplosionEffect

class Soldier:
    def __init__(self, x, y):
        self.x, self.y = float(x), float(y)
        self.facing_right = True
        self.anims = {anim: load_spritesheet(anim, fc) for anim, fc in ANIM_FRAMES.items()}
        self.current_anim = "Idle"
        self.frame_index = 0
        self.frame_timer = 0
        self.ammo = MAX_AMMO
        self.grenades = MAX_GRENADES
        self.health = 100.0
        self.is_shooting = False
        self.is_reloading = False
        self.is_throwing = False
        self.action_spawned = False
        self.bullets = []
        self.projectiles = []
        self.foot_r = 18
        self.is_dead = False

    def shoot(self, active=True):
        if self.is_reloading or self.is_throwing or self.is_dead: return
        if self.ammo <= 0: active = False
        if active and not self.is_shooting:
            self.is_shooting = True
            self.set_animation("Shot_2")
            self.action_spawned = False

    def reload(self):
        if not self.is_reloading and not self.is_throwing and self.ammo < MAX_AMMO:
            self.is_reloading = True
            self.set_animation("Recharge")

    def throw_grenade(self):
        if not self.is_throwing and self.grenades > 0:
            self.is_throwing = True
            self.set_animation("Grenade")
            self.action_spawned = False

    def set_animation(self, name):
        if name not in self.anims or not self.anims[name]: return
        if name != self.current_anim:
            self.current_anim = name
            self.frame_index = 0
            self.frame_timer = 0

    def foot_rect(self, x=None, y=None):
        fx = x if x is not None else self.x
        fy = y if y is not None else self.y
        return pygame.Rect(fx - self.foot_r, fy - self.foot_r, self.foot_r * 2, self.foot_r * 2)

    def update(self, keys, obstacles, jx=0.0, jy=0.0, pad_sprint=False):
        # Update projectiles
        for b in self.bullets[:]:
            b.update(obstacles)
            if not b.alive: self.bullets.remove(b)
        for g in self.projectiles[:]:
            g.update(obstacles)
            if isinstance(g, GrenadeProjectile) and g.has_exploded:
                self.projectiles.remove(g)
                if "Explosion" in self.anims:
                    self.projectiles.append(ExplosionEffect(g.x, g.y, self.anims["Explosion"]))
            elif not g.alive:
                self.projectiles.remove(g)

        # Death Animation Lock
        if self.health <= 0:
            if not self.is_dead:
                self.is_dead = True
                self.set_animation("Dead")
            self.frame_timer += 1
            if self.frame_timer >= ANIM_SPEED.get("Dead", 8):
                self.frame_timer = 0
                if self.frame_index < len(self.anims.get("Dead", [])) - 1:
                    self.frame_index += 1
            return

        # Movement with LOOK AHEAD
        run = (keys[pygame.K_LSHIFT] or pad_sprint) and not self.is_reloading
        spd = SPEED * (1.7 if run else 1.0)
        if self.is_reloading: spd *= 0.6
        
        vx, vy = 0.0, 0.0
        
        # Hit Stun check
        hit_stunned = getattr(self, "hit_stun", 0) > 0
        if hit_stunned:
            self.hit_stun -= 1
            if getattr(self, "health", 100) > 0:
                self.set_animation("Hurt")
        else:
            if keys[pygame.K_LEFT]  or keys[pygame.K_a]: vx = -spd; self.facing_right = False
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]: vx =  spd; self.facing_right = True
            if keys[pygame.K_UP]    or keys[pygame.K_w]: vy = -spd
            if keys[pygame.K_DOWN]  or keys[pygame.K_s]: vy =  spd
            
            # Mobile Joystick Override
            if jx != 0 or jy != 0:
                vx = jx * spd
                vy = jy * spd
                if jx < -0.1: self.facing_right = False
                elif jx > 0.1: self.facing_right = True
                
            if vx and vy and (jx == 0 and jy == 0): vx *= 0.707; vy *= 0.707

            # Look Ahead Collision Detection (smoother navigation)
            look_dist = 20
            nx = self.x + vx
            if vx != 0:
                lx = self.x + (vx / abs(vx)) * look_dist
                if any(self.foot_rect(lx, self.y).colliderect(ob) for ob in obstacles):
                    vx = 0
                elif not any(self.foot_rect(nx, self.y).colliderect(ob) for ob in obstacles):
                    self.x = nx
            
            ny = self.y + vy
            if vy != 0:
                ly = self.y + (vy / abs(vy)) * look_dist
                if any(self.foot_rect(self.x, ly).colliderect(ob) for ob in obstacles):
                    vy = 0
                elif not any(self.foot_rect(self.x, ny).colliderect(ob) for ob in obstacles):
                    self.y = ny

            # Animation logic
            if not self.is_throwing and not self.is_reloading:
                if self.is_shooting and not (vx or vy):
                    self.set_animation("Shot_2")
                else:
                    moving = abs(vx) > 0.1 or abs(vy) > 0.1
                    self.set_animation("Run" if (run and moving) else "Walk" if moving else "Idle")

        # Frame advancement
        self.frame_timer += 1
        if self.frame_timer >= ANIM_SPEED.get(self.current_anim, 8):
            self.frame_timer = 0
            self.frame_index += 1

            # Actions based on frame
            if not self.action_spawned and not hit_stunned:
                if self.is_shooting and self.frame_index == 1:
                    side = 1 if self.facing_right else -1
                    # Military precise barrel offset
                    self.bullets.append(Bullet(self.x + side * 45 * SCALE, self.y - 42 * SCALE, self.facing_right))
                    self.ammo -= 1; self.action_spawned = True
                elif self.is_throwing and self.frame_index == 6:
                    self.projectiles.append(GrenadeProjectile(self.x, self.y - 45 * SCALE, self.facing_right, self.anims.get("Explosion", [])))
                    self.grenades -= 1; self.action_spawned = True

            # End of animation cycle
            frames = self.anims.get(self.current_anim, [])
            if self.frame_index >= len(frames):
                if self.current_anim == "Hurt":
                    self.frame_index = len(frames) - 1 # Pause at end of hurt frame if still stunned
                else:
                    self.frame_index = 0
                    if self.is_reloading: 
                        self.is_reloading = False
                        self.ammo = MAX_AMMO
                        self._reload_done = True  # Signal to main.py for audio
                    elif self.is_throwing: self.is_throwing = False
                    elif self.is_shooting: self.is_shooting = False

    def draw(self, surface, cam):
        sx, sy = cam.apply(self.x, self.y)
        pygame.draw.ellipse(surface, (0, 0, 0, 90), (sx - 32, sy - 10, 64, 20))

        for b in self.bullets: b.draw(surface, cam)
        for g in self.projectiles: g.draw(surface, cam)

        frames = self.anims.get(self.current_anim, [])
        if not frames: return
        idx = min(self.frame_index, len(frames) - 1)
        frame = frames[idx]
        if not self.facing_right: frame = pygame.transform.flip(frame, True, False)

        # STABLE DRAW: midbottom is rock solid with the new Union-Crop alg in utils.py
        fr = frame.get_rect()
        fr.midbottom = (sx, sy)
        surface.blit(frame, fr.topleft)
