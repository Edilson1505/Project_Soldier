import pygame
from src.ui.elements.base import MenuButton

class PauseMenu:
    def __init__(self):
        self.r_btn = MenuButton(0, -60, 420, 80, "RESUME OPERATION", is_right=False)
        self.q_btn = MenuButton(0, 60, 420, 80, "MAIN MENU", is_right=False)
    def update(self, sw, sh):
        if self.r_btn.update(sw, sh): return "resume"
        if self.q_btn.update(sw, sh): return "quit"
        return None
    def draw(self, surface):
        sw, sh = surface.get_size() ; ov = pygame.Surface((sw, sh), pygame.SRCALPHA); ov.fill((0, 0, 0, 180)); surface.blit(ov, (0, 0))
        self.r_btn.draw(surface); self.q_btn.draw(surface)
