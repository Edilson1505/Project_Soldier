import pygame
import math
import random
from src.core.settings import SPEED, ANIM_SPEED, SCALE, WALL_T, ROOM_W, ROOM_H, PADDING
from src.core.paths import get_safe_font
from src.entities.projectiles import Bullet

NAMES = ["SGT. RED", "CPL. PHOENIX", "SHADOW", "STALKER", "ELITE BRAVO", "GHOST-7", "DELTA-9"]

class EnemySoldier:
    def __init__(self, x, y, anims):
        self.x, self.y = float(x), float(y)
        self.anims = anims
        self.current_anim = "Idle"
        self.frame_index = 0
        self.frame_timer = 0
        self.facing_right = True
        self.health = 100.0
        self.alive = True
        self.is_dead = False
        self.name = random.choice(NAMES)
        self.foot_r = 18
        self.detect_range = 350
        self.attack_range = 250
        self.shoot_cd = random.randint(50, 110)
        self.bullets = []
        self.f_label = get_safe_font("Consolas", 14, bold=True)
        self.hit_stun = 0

    def foot_rect(self, x=None, y=None):
        fx = x if x is not None else self.x
        fy = y if y is not None else self.y
        return pygame.Rect(fx - self.foot_r, fy - self.foot_r, self.foot_r * 2, self.foot_r * 2)

    def set_animation(self, n):
        if n not in self.anims or not self.anims[n]: return
        if n != self.current_anim:
            self.current_anim = n; self.frame_index = 0; self.frame_timer = 0

    def take_damage(self, amt):
        self.health -= amt
        if self.health <= 0: 
            self.alive = False
        else:
            self.hit_stun = 20 # frames of stun
            self.set_animation("Hurt")

    def update(self, px, py, obstacles):
        # Process bullets regardless if dead or not
        for b in self.bullets[:]:
            b.update(obstacles)
            if not b.alive: self.bullets.remove(b)

        # Death sequence
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

        if not self.alive: return

        # Process hit stun
        if self.hit_stun > 0:
            self.hit_stun -= 1
            if self.current_anim != "Hurt":
                self.set_animation("Hurt")
            self.frame_timer += 1
            if self.frame_timer >= ANIM_SPEED.get("Hurt", 4):
                self.frame_timer = 0
                frames = self.anims.get("Hurt", [])
                if frames:
                    # Stop at the last frame of Hurt if stun is long, or loop it
                    self.frame_index = min(self.frame_index + 1, len(frames) - 1)
            return # Skip all movement and shooting while stunned

        dist = math.hypot(px - self.x, py - self.y)
        vx, vy = 0.0, 0.0

        if dist < self.detect_range:
            angle = math.atan2(py - self.y, px - self.x)
            self.facing_right = px > self.x
            
            # AI Strafe logic (move perpendicular when at good range)
            # Create a simple strafe direction that flips occasionally
            if getattr(self, "strafe_dir", 0) == 0:
                self.strafe_dir = random.choice([-1, 1])
                self.strafe_timer = random.randint(30, 90)
            
            self.strafe_timer -= 1
            if self.strafe_timer <= 0:
                self.strafe_dir = random.choice([-1, 1])
                self.strafe_timer = random.randint(30, 90)

            # Navigation logic
            if dist > self.attack_range - 60:
                # Approach
                s = SPEED * (1.15 if dist < self.detect_range * 0.45 else 0.7)
                vx = math.cos(angle) * s
                vy = math.sin(angle) * s
                # Add slight strafe while approaching
                vx += math.cos(angle + math.pi/2) * s * 0.4 * self.strafe_dir
                vy += math.sin(angle + math.pi/2) * s * 0.4 * self.strafe_dir
            elif dist < 140:
                # Back away
                s = SPEED * 0.5
                vx = -math.cos(angle) * s
                vy = -math.sin(angle) * s
            else:
                # Maintain distance and strafe (sidestep)
                s = SPEED * 0.75
                vx = math.cos(angle + math.pi/2) * s * self.strafe_dir
                vy = math.sin(angle + math.pi/2) * s * self.strafe_dir

            # Shoot logic
            if dist < self.attack_range and self.shoot_cd <= 0:
                side = 1 if self.facing_right else -1
                # Adjusted bullet spawn Y closer to gun barrel (-42)
                self.bullets.append(Bullet(self.x + side * 30 * SCALE, self.y - 42 * SCALE, self.facing_right))
                self.shoot_cd = 85

        if self.shoot_cd > 0: self.shoot_cd -= 1

        # LOOK AHEAD COLLISION
        look_dist = 30
        
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

        moving = abs(vx) > 0.1 or abs(vy) > 0.1
        
        # Priority: Animation matches action
        if self.shoot_cd > 60:
            vx, vy = 0.0, 0.0 # Force stop while shooting
            self.x = nx if not vx == 0 else self.x
            self.y = ny if not vy == 0 else self.y
            self.set_animation("Shot_2")
        elif moving:
            self.set_animation("Run" if dist < self.detect_range * 0.45 else "Walk")
        else:
            self.set_animation("Idle")

        self.frame_timer += 1
        if self.frame_timer >= ANIM_SPEED.get(self.current_anim, 8):
            self.frame_timer = 0
            frames = self.anims.get(self.current_anim, [])
            if frames: self.frame_index = (self.frame_index + 1) % len(frames)

    def draw(self, surface, cam):
        if not self.alive: return
        sx, sy = cam.apply(self.x, self.y)

        frames = self.anims.get(self.current_anim, [])
        if not frames: return
        idx = min(self.frame_index, len(frames) - 1)
        frame = frames[idx]
        if not self.facing_right:
            frame = pygame.transform.flip(frame, True, False)

        fr = frame.get_rect()
        fr.midbottom = (sx, sy)
        # Removed the ugly white flash blending code
        surface.blit(frame, fr.topleft)

        pygame.draw.ellipse(surface, (0, 0, 0, 60), (sx - 32, sy - 10, 64, 20))

        label_y = fr.top - 20
        pygame.draw.rect(surface, (40, 50, 60), (sx - 25, label_y, 50, 4))
        pygame.draw.rect(surface, (230, 60, 60), (sx - 25, label_y, int(50 * (self.health/60.0)), 4))
        name_surf = self.f_label.render(self.name, True, (240, 245, 255))
        surface.blit(name_surf, (sx - name_surf.get_width()//2, label_y - 16))
