import pygame
import math
from ..elements.base import TextInput, MenuButton, AmbientParticle
from ...core.settings import SCREEN_W, SCREEN_H
from ...core.paths import get_asset_path, get_safe_font

class LoginMenu:
    def __init__(self):
        try: self.bg = pygame.image.load(get_asset_path("login_portait_bg.png")).convert_alpha()
        except: self.bg = None
        self.name_in = TextInput(180, 500, 75, "ENTER CREDENTIALS (Name)")
        self.btn = MenuButton(0, 280, 400, 75, "UNLOCK ACCESS", is_right=False)
        self.t_font = get_safe_font("Consolas", 72, bold=True) 
        self.sub_font = get_safe_font("Consolas", 24, bold=True)
        self.time = 0.0
        self.ambient = [AmbientParticle(SCREEN_W, SCREEN_H) for _ in range(120)]

    def update(self, events):
        sw, sh = pygame.display.get_surface().get_size() 
        self.time += 0.05
        self.ambient = [p for p in self.ambient if p.update()]
        if len(self.ambient) < 140: self.ambient.append(AmbientParticle(sw, sh))
        self.name_in.update(events, sw, sh)
        if self.btn.update(sw, sh): return "login"
        return None

    def draw(self, surface):
        sw, sh = surface.get_size() ; surface.fill((8, 10, 12))
        if self.bg:
            ox = math.sin(self.time) * 15 ; bh = sh + 60
            bw = int(self.bg.get_width() * (bh / self.bg.get_height()))
            # Darker, grittier blend for the login background
            bg_scaled = pygame.transform.scale(self.bg, (bw, bh))
            surface.blit(bg_scaled, (-30 + ox, -30))
            
            overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
            overlay.fill((5, 12, 10, 180)) # Dark tactical green wash
            surface.blit(overlay, (0, 0))
            
            # Animated heavy scanlines
            scan_y = int((self.time * 40) % sh)
            pygame.draw.rect(surface, (150, 200, 120, 15), (0, scan_y, sw, 80))
            for i in range(0, sh, 5): pygame.draw.line(surface, (0, 0, 0, 60), (0, i), (sw, i))

        for p in self.ambient: p.draw(surface)
        
        # Center Console Alignment
        cx, cy = sw//2, sh//2 - 120
        
        t1_shadow = self.t_font.render("SECURITY TERMINAL", True, (0,0,0))
        t1 = self.t_font.render("SECURITY TERMINAL", True, (200, 230, 200))
        surface.blit(t1_shadow, (cx - t1.get_width()//2 + 4, cy - 140 + 4))
        surface.blit(t1, (cx - t1.get_width()//2, cy - 140))
        
        # Pulsing Subtitle
        pulse = int(100 + 155 * math.sin(self.time*5))
        pulse = max(0, min(255, pulse))
        t2 = self.sub_font.render("SYSTEM LOCKED - ACCESS RESTRICTED", True, (255, pulse//2, pulse//2))
        surface.blit(t2, (cx - t2.get_width()//2, cy - 50))
        
        # Decorative tactical rules
        pygame.draw.line(surface, (150, 200, 120, 100), (cx - 250, cy - 10), (cx + 250, cy - 10), 2)
        pygame.draw.rect(surface, (150, 200, 120), (cx - 250, cy - 13, 10, 8))
        pygame.draw.rect(surface, (150, 200, 120), (cx + 240, cy - 13, 10, 8))

        self.name_in.draw(surface) 
        self.btn.draw(surface)
