import pygame
from ..core.settings import DISPLAY_SIZE, SCALE, ANIM_FRAMES, ANIM_SPEED
from ..core.utils import load_spritesheet
from ..core.paths import get_safe_font

class TacticalDummy:
    def __init__(self, x, y):
        self.x, self.y = float(x), float(y)
        self.anims = {anim: load_spritesheet(anim, fc) for anim, fc in ANIM_FRAMES.items()}
        self.current_anim = "Idle" ; self.frame_index = 0 ; self.frame_timer = 0
        self.health = 500 ; self.is_dead = False ; self.death_timer = 0
        self.hit_w, self.hit_h = 50, 100
        # Rectangulo de colisión basado en pies
        self.hitbox = pygame.Rect(self.x - 25, self.y - 100, 50, 100)
        # Pre-cache the font for better performance
        self.font = get_safe_font("Consolas", 14, bold=True)
    
    def take_damage(self, amt):
        self.health -= amt
        if self.health <= 0: self.is_dead = True ; self.set_animation("Explosion")

    def set_animation(self, n):
        if n != self.current_anim: self.current_anim = n ; self.frame_index = 0 ; self.timer = 0

    def update(self):
        if self.is_dead:
            self.death_timer += 1
            if self.death_timer > 300: self.health = 500 ; self.is_dead = False ; self.set_animation("Idle") ; self.death_timer = 0
        
        self.hitbox = pygame.Rect(self.x - 25, self.y - 100, 50, 100)
        self.frame_timer += 1
        if self.frame_timer >= ANIM_SPEED.get(self.current_anim, 8):
            self.frame_timer = 0 ; self.frame_index += 1
            if self.frame_index >= len(self.anims[self.current_anim]):
                self.frame_index = 0 if not self.is_dead else len(self.anims[self.current_anim])-1
    
    def draw(self, surface, cam):
        # 🦶 ANCLAJE CENTRAL INFERIOR
        sx, sy = cam.apply(self.x, self.y)
        pygame.draw.ellipse(surface, (0, 0, 0, 55), (sx - 50, sy - 12, 100, 24))
        
        if not self.is_dead:
            pygame.draw.rect(surface, (40, 0, 0), (sx - 40, sy - 140, 80, 6))
            pygame.draw.rect(surface, (100, 150, 255), (sx - 40, sy - 140, int(80 * (self.health/500)), 6))
            txt = self.font.render("DUMMY [TACTICO]", True, (150, 180, 255))
            surface.blit(txt, (sx - txt.get_width()//2, sy - 160))

        frame = self.anims[self.current_anim][self.frame_index]
        dummy_f = frame.copy() ; dummy_f.fill((100, 150, 255, 255), special_flags=pygame.BLEND_RGBA_MULT)
        
        # 🦶 CENTRAR Y ANCLAR A LA BASE
        fr = dummy_f.get_rect()
        fr.midbottom = (sx, sy)
        surface.blit(dummy_f, fr.topleft)
