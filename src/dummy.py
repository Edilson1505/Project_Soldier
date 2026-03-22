import pygame
import random
from .settings import DISPLAY_SIZE, ANIM_FRAMES, ANIM_SPEED, SCALE
from .utils import load_spritesheet

class TacticalDummy:
    def __init__(self, x, y):
        self.x, self.y = float(x), float(y)
        self.max_hp = 100 ; self.hp = 100
        names = ["Sgt. Ghost", "Lt. Price", "Delta Bravo", "Soap", "Viper-1", "Grizzly"]
        self.name = random.choice(names)
        self.font = pygame.font.SysFont("Consolas", 18, bold=True)
        self.anims = {
            "Idle": load_spritesheet("Idle", ANIM_FRAMES["Idle"]),
            "Hurt": load_spritesheet("Hurt", ANIM_FRAMES["Hurt"]),
            "Dead": load_spritesheet("Dead", ANIM_FRAMES["Dead"]),
        }
        self.current_anim = "Idle" ; self.frame_index = 0 ; self.frame_timer = 0
        self.is_dead = False ; self.is_hurt = False ; self.respawn_timer = 0
        self.hitbox = pygame.Rect(self.x + 30*SCALE, self.y + 20*SCALE, 68*SCALE, 95*SCALE)
        self.feet_hitbox = pygame.Rect(self.x + 45*SCALE, self.y + 100*SCALE, 38*SCALE, 15*SCALE)

    def set_animation(self, name):
        if self.current_anim != name:
            self.current_anim = name ; self.frame_index = 0 ; self.frame_timer = 0

    def take_damage(self, amount):
        if self.is_dead: return
        self.hp = max(0, self.hp - amount)
        if self.hp <= 0:
            self.is_dead = True ; self.is_hurt = False ; self.set_animation("Dead")
            self.respawn_timer = 180
        else:
            self.is_hurt = True ; self.set_animation("Hurt")

    def update(self):
        self.frame_timer += 1
        speed = ANIM_SPEED[self.current_anim]
        if self.frame_timer >= speed:
            self.frame_timer = 0 ; self.frame_index += 1
            frames = self.anims[self.current_anim]
            if self.frame_index >= len(frames):
                if self.is_dead: self.frame_index = len(frames) - 1
                elif self.is_hurt: self.is_hurt = False ; self.set_animation("Idle")
                else: self.frame_index = 0
        if self.is_dead:
            self.respawn_timer -= 1
            if self.respawn_timer <= 0:
                self.hp = self.max_hp ; self.is_dead = False ; self.set_animation("Idle")
        self.hitbox.topleft = (self.x + 30*SCALE, self.y + 20*SCALE)
        self.feet_hitbox.topleft = (self.x + 45*SCALE, self.y + 100*SCALE)

    def draw(self, surface, cam):
        sx, sy = cam.apply(self.x, self.y)
        
        # 🌑 SOMBRA BAJADA Y CENTRADA (sy + DISPLAY_SIZE - 4)
        sh_x, sh_y = sx + (DISPLAY_SIZE // 2) - 10, sy + DISPLAY_SIZE - 4
        pygame.draw.ellipse(surface, (0, 0, 0, 65), (sh_x - 50, sh_y - 12, 100, 24))
        
        f = self.anims[self.current_anim][self.frame_index]
        if self.is_hurt:
            tint = f.copy() ; tint.fill((255, 100, 100), special_flags=pygame.BLEND_RGB_MULT)
            surface.blit(tint, (sx, sy))
        else:
            surface.blit(f, (sx, sy))

        if not self.is_dead:
            name_txt = self.font.render(self.name, True, (255, 255, 180))
            surface.blit(name_txt, (sx + (DISPLAY_SIZE//2) - name_txt.get_width()//2, sy + 90))
            bw, bh = 110, 6
            bx, by = sx + (DISPLAY_SIZE//2) - bw//2, sy + 120
            pygame.draw.rect(surface, (10, 10, 15), (bx, by, bw, bh), border_radius=2)
            hp_w = int(bw * (self.hp / self.max_hp))
            hp_c = (255, 255, 255) if self.hp > 30 else (255, 50, 50)
            pygame.draw.rect(surface, hp_c, (bx, by, hp_w, bh), border_radius=2)
            pygame.draw.rect(surface, (120, 120, 120), (bx, by, bw, bh), 1, border_radius=2)
        else:
            die_txt = self.font.render("TARGET DOWN", True, (255, 50, 50))
            surface.blit(die_txt, (sx + (DISPLAY_SIZE//2) - die_txt.get_width()//2, sy + 110))
