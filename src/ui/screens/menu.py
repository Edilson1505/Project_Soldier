import pygame
import math
from ..elements.base import MenuButton
from ...core.paths import get_asset_path, get_safe_font

class MainMenu:
    def __init__(self):
        try:
            self.bg = pygame.image.load(get_asset_path("main_portait_bg.png")).convert()
        except:
            self.bg = None
        self.title_f = get_safe_font("Consolas", 90, bold=True)
        self.btns = {
            "solo": MenuButton(240, -60, 480, 80, "START OPERATION"),
            "lan":  MenuButton(240, 60, 480, 80, "LOCAL SYSTEM"),
            "prof": MenuButton(240, 180, 480, 80, "OPERATOR PROFILE"),
            "exit": MenuButton(240, 300, 220, 60, "ABANDON", small=True)
        }
        self.time = 0.0
        self.grad_cache = None

    def _create_gradient(self, sw, sh):
        # Stronger, wider shadow blend for the right side
        sh_width = 850
        grad = pygame.Surface((sh_width, sh), pygame.SRCALPHA).convert_alpha()
        for i in range(sh_width):
            # Non-linear alpha for a smoother "smoke" blend feel
            alpha = int(math.pow(i / sh_width, 1.5) * 255)
            pygame.draw.line(grad, (4, 4, 8, alpha), (i, 0), (i, sh))
        return grad

    def update(self):
        sw, sh = pygame.display.get_surface().get_size()
        self.time += 0.02
        actions = []
        for name, btn in self.btns.items():
            if btn.update(sw, sh):
                actions.append(name)
        return actions

    def draw(self, surface):
        sw, sh = surface.get_size()
        surface.fill((4, 4, 10))
        
        if self.bg:
            # Subtle parallax / slide
            ox = math.sin(self.time * 0.5) * 20
            bh = sh + 40
            bw = int(self.bg.get_width() * (bh / self.bg.get_height()))
            bg_scaled = pygame.transform.scale(self.bg, (bw, bh))
            surface.blit(bg_scaled, (-30 + ox, -20))
            
            # Shadow Blend (Gradient)
            if self.grad_cache is None or self.grad_cache.get_height() != sh:
                self.grad_cache = self._create_gradient(sw, sh)
            surface.blit(self.grad_cache, (sw - 850, 0))
        
        # Solid right panel for buttons
        pygame.draw.rect(surface, (4, 4, 10), (sw - 500, 0, 500, sh))
        
        # English Title with Shadow
        t_shadow = self.title_f.render("PROJECT", True, (0, 0, 0))
        t = self.title_f.render("PROJECT", True, (240, 245, 255))
        s_shadow = self.title_f.render("SOLDIER", True, (0, 0, 0))
        s = self.title_f.render("SOLDIER", True, (150, 200, 120)) # Tactical Green Soldier
        
        tx, ty = sw - 280, 100
        surface.blit(t_shadow, (tx - t.get_width()//2 + 4, ty + 4))
        surface.blit(t, (tx - t.get_width()//2, ty))
        
        sx, sy = sw - 280, 200
        surface.blit(s_shadow, (sx - s.get_width()//2 + 4, sy + 4))
        surface.blit(s, (sx - s.get_width()//2, sy))
        
        for btn in self.btns.values():
            btn.draw(surface)
