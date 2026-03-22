import pygame
from .elements.base import UIButton
from .screens.login import LoginMenu
from .screens.menu import MainMenu
from .screens.profile import ProfileScreen
from .screens.avatar import AvatarSelection
from .screens.lan import LANMenu
from .screens.hud import TacticalHUD
from .screens.pause import PauseMenu

class GameUI:
    def __init__(self, soldier):
        self.soldier = soldier
        self.particles = []
        self.login_menu = LoginMenu()
        self.main_menu = MainMenu()
        self.prof_screen = None 
        self.avatar_sel = AvatarSelection()
        self.lan_menu = LANMenu()
        self.hud = TacticalHUD(soldier)
        self.p_menu = PauseMenu()
        
        # Cinematic cache
        self.vignette = None
        
        self.buttons = {
            "shoot":   UIButton(2, 2, -150, -150, 80, "shoot"),
            "grenade": UIButton(2, 2, -180, -320, 45, "grenade"),
            "reload":  UIButton(2, 2, -320, -180, 45, "reload"),
            "run":     UIButton(0, 2, 380, -140, 40, "run"),
            "pause":   UIButton(1, 0, 0, 55, 30, "pause")
        }

    def _draw_cinematic(self, surface, scanlines=True, vignette_strength=1.0):
        """
        Draws the bunker cinematic effects.
        vignette_strength: multiplier for the alpha of the corner shadow (0.0 to 1.0)
        """
        sw, sh = surface.get_size()
        
        # 1. Vignette (Dark Corners) - Adjusted for much softer intensity (user requested lower shadow)
        if self.vignette is None or self.vignette.get_size() != (sw, sh):
            self.vignette = pygame.Surface((sw, sh), pygame.SRCALPHA).convert_alpha()
            for i in range(0, sw, 8):
                for j in range(0, sh, 8):
                    dx = (i - sw/2) / (sw/2)
                    dy = (j - sh/2) / (sh/2)
                    dist = (dx*dx + dy*dy) ** 0.5
                    if dist > 0.4:
                        # Max alpha reduced to 80 for very subtle military effect
                        alpha = int(min(80, (dist - 0.4) * 160))
                        pygame.draw.rect(self.vignette, (0, 0, 4, alpha), (i, j, 8, 8))
        
        # Draw vignette with strength multiplier
        if vignette_strength > 0:
            if vignette_strength == 1.0:
                surface.blit(self.vignette, (0, 0))
            else:
                temp_v = self.vignette.copy()
                temp_v.fill((255, 255, 255, int(255 * vignette_strength)), special_flags=pygame.BLEND_RGBA_MULT)
                surface.blit(temp_v, (0, 0))

        # 2. Subtle Scanlines
        if scanlines:
            for y in range(0, sh, 4):
                line = pygame.Surface((sw, 1), pygame.SRCALPHA)
                line.fill((0, 0, 10, 15)) # Reduced opacity from 30 to 15
                surface.blit(line, (0, y))

    def update_login(self, evs):  return self.login_menu.update(evs)
    def update_main(self):       return self.main_menu.update()
    def update_lan(self):        return self.lan_menu.update()
    def update_prof(self):       return self.prof_screen.update()
    def update_avatar(self):     return self.avatar_sel.update()

    def draw_login(self, s):  
        self.login_menu.draw(s)
        # Login and sub-screens keep the cinematic look but with reduced shadow
        self._draw_cinematic(s, scanlines=True, vignette_strength=0.7)
        
    def draw_main(self, s):   
        self.main_menu.draw(s)
        self._draw_cinematic(s, scanlines=True, vignette_strength=0.7)
        
    def draw_lan(self, s):    
        self.lan_menu.draw(s)
        self._draw_cinematic(s, scanlines=True, vignette_strength=0.7)
        
    def draw_prof(self, s):   
        self.prof_screen.draw(s)
        self._draw_cinematic(s, scanlines=True, vignette_strength=0.7)
        
    def draw_avatar(self, s): 
        self.avatar_sel.draw(s)
        self._draw_cinematic(s, scanlines=True, vignette_strength=0.7)

    def update(self, is_paused):
        sw, sh = pygame.display.get_surface().get_size()
        self.particles = [p for p in self.particles if p.update()]
        if is_paused: return self.p_menu.update(sw, sh)
        
        actions = []
        for name, btn in self.buttons.items():
            if btn.update(sw, sh, self.particles): actions.append(name)
        return actions

    def draw(self, surface, is_paused):
        sw, sh = surface.get_size()
        if is_paused:
            self.p_menu.draw(surface)
            # Pause menu can keep a very subtle vignette but no scanlines
            self._draw_cinematic(surface, scanlines=False, vignette_strength=0.5)
            return
        
        self.hud.draw(surface, sw, sh, self.hud.enemies_ref)
        for b in self.buttons.values(): b.draw(surface)
        for p in self.particles: p.draw(surface)
        # Solo mode (playing) - Cinematic removed as requested
        # No _draw_cinematic call here
