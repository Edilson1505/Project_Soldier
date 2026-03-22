import pygame
import math
from ..elements.base import MenuButton
from ...core.paths import get_safe_font

class LANMenu:
    def __init__(self):
        self.title_f = get_safe_font("Consolas", 56, bold=True)
        self.sub_f = get_safe_font("Consolas", 18, bold=True)
        self.time = 0.0
        self.btns = {
            "create": MenuButton(0, -60, 480, 85, "DEPLOY / CREATE LOBBY", is_right=False),
            "join":   MenuButton(0, 50, 480, 85, "SEARCH & JOIN", is_right=False),
            "back":   MenuButton(0, 220, 240, 65, "ABORT", is_right=False, small=True)
        }
        # Military Palette
        self.BG_COLOR = (12, 16, 14)
        self.PANEL_BG = (22, 28, 24)
        self.ACCENT   = (150, 200, 120)

    def update(self):
        self.time += 0.05
        sw, sh = pygame.display.get_surface().get_size()
        actions = []
        for name, btn in self.btns.items():
            if btn.update(sw, sh): actions.append(name)
        return actions

    def draw(self, surface):
        sw, sh = surface.get_size()
        surface.fill(self.BG_COLOR)
        
        # Grid Background
        for x in range(0, sw, 80): pygame.draw.line(surface, (20, 25, 20), (x, 0), (x, sh))
        for y in range(0, sh, 80): pygame.draw.line(surface, (20, 25, 20), (0, y), (sw, y))

        pw, ph = 600, 550
        px, py = sw//2 - pw//2, sh//2 - ph//2 + 30
        
        # Drop Shadow
        pygame.draw.rect(surface, (0, 0, 0, 150), (px+10, py+10, pw, ph), border_radius=8)
        
        # Tactical Panel Base
        pygame.draw.rect(surface, self.PANEL_BG, (px, py, pw, ph), border_radius=8)
        
        # Scanlines inside panel
        s = pygame.Surface((pw, ph), pygame.SRCALPHA)
        for i in range(0, ph, 4): pygame.draw.line(s, (0, 0, 0, 60), (0, i), (pw, i))
        surface.blit(s, (px, py))
        
        # 3D Highlight / Bevel
        pygame.draw.rect(surface, (40, 50, 40), (px, py, pw, ph), 2, border_radius=8)
        pygame.draw.line(surface, self.ACCENT, (px, py+15), (px, py+50), 4)

        # Title
        title_y = py - 80
        t_shadow = self.title_f.render("TACTICAL NETWORK", True, (0, 0, 0))
        t_txt = self.title_f.render("TACTICAL NETWORK", True, (240, 250, 240))
        surface.blit(t_shadow, (sw//2 - t_txt.get_width()//2 + 4, title_y + 4))
        surface.blit(t_txt, (sw//2 - t_txt.get_width()//2, title_y))

        # Subtitle blinking
        if int(self.time * 4) % 2 == 0:
            sub = self.sub_f.render("SEARCHING FOR SECURE CONNECTIONS...", True, self.ACCENT)
            surface.blit(sub, (sw//2 - sub.get_width()//2, py+20))

        for btn in self.btns.values(): btn.draw(surface)
