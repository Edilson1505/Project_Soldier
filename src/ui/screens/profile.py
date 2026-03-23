import pygame
from src.ui.elements.base import MenuButton
from src.core.paths import get_asset_path, get_safe_font

class ProfileScreen:
    def __init__(self, username, img_file):
        self.user = username
        self.img_file = img_file
        self.time = 0.0
        self.btn_edit = MenuButton(0, 190, 420, 75, "MODIFY ASSIGNMENT", is_right=False)
        self.btn_back = MenuButton(0, 290, 220, 60, "ABORT", is_right=False, small=True)
        self.f_big = get_safe_font("Consolas", 56, bold=True)
        self.f_sub = get_safe_font("Consolas", 18, bold=True)
        
        # Military Palette
        self.BG_COLOR = (12, 16, 14)
        self.PANEL_BG = (22, 28, 24)
        self.ACCENT   = (150, 200, 120)
        
        self.image = None
        self._load_image()

    def _load_image(self):
        try:
            img = pygame.image.load(get_asset_path(self.img_file)).convert()
            size = min(img.get_width(), img.get_height())
            rect = pygame.Rect((img.get_width() - size)//2, (img.get_height() - size)//2, size, size)
            cropped = img.subsurface(rect).copy()
            self.image = pygame.transform.scale(cropped, (220, 220))
        except:
            self.image = pygame.Surface((220, 220))
            self.image.fill((40, 50, 45))
            pygame.draw.circle(self.image, (100, 120, 100), (110, 110), 80, 5)

    def update(self):
        self.time += 0.05
        sw, sh = pygame.display.get_surface().get_size()
        if self.btn_edit.update(sw, sh): return "edit"
        if self.btn_back.update(sw, sh): return "back"
        return None

    def draw(self, surface):
        sw, sh = surface.get_size()
        surface.fill(self.BG_COLOR)
        
        # Grid Background
        for x in range(0, sw, 80): pygame.draw.line(surface, (20, 25, 20), (x, 0), (x, sh))
        for y in range(0, sh, 80): pygame.draw.line(surface, (20, 25, 20), (0, y), (sw, y))

        card_w, card_h = 760, 380
        card = pygame.Rect(sw//2 - card_w//2, sh//2 - card_h//2 - 60, card_w, card_h)
        
        # Drop Shadow
        pygame.draw.rect(surface, (0, 0, 0, 150), card.move(10, 10), border_radius=8)
        
        # Dossier Panel Base
        pygame.draw.rect(surface, self.PANEL_BG, card, border_radius=8)
        
        # Scanlines inside panel
        s = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        for i in range(0, card_h, 4): pygame.draw.line(s, (0, 0, 0, 60), (0, i), (card_w, i))
        surface.blit(s, card.topleft)
        
        # 3D Highlight & Industrial Screws
        pygame.draw.rect(surface, (40, 50, 40), card, 2, border_radius=8)
        screws = [(card.left+15, card.top+15), (card.right-15, card.top+15), 
                  (card.left+15, card.bottom-15), (card.right-15, card.bottom-15)]
        for sx, sy in screws: pygame.draw.circle(surface, (10, 15, 12), (sx, sy), 4)

        # Avatar Window
        av_w = 220
        av_rect = pygame.Rect(card.x + 40, card.y + 80, av_w, av_w)
        pygame.draw.rect(surface, (0, 0, 0, 180), av_rect.move(6,6), border_radius=6) # shadow
        
        if self.image:
            surface.blit(self.image, av_rect.topleft)
            
        pygame.draw.rect(surface, self.ACCENT, av_rect, 3, border_radius=6)

        # Text Layout
        tx = card.x + 300
        ty = card.y + 60
        
        # "Classified" stamp blinking
        if int(self.time * 2) % 2 == 0:
            stamp = get_safe_font("Consolas", 28, bold=True).render("CLASSIFIED", True, (180, 40, 40))
            stamp.set_alpha(150)
            surface.blit(pygame.transform.rotate(stamp, 15), (card.right - 180, card.top + 50))

        surface.blit(self.f_sub.render("DOSSIER: MILITARY OPERATIVE", True, self.ACCENT), (tx, ty))
        
        n_shadow = self.f_big.render(self.user.upper(), True, (0, 0, 0))
        n_txt = self.f_big.render(self.user.upper(), True, (240, 250, 240))
        surface.blit(n_shadow, (tx + 3, ty + 30 + 3))
        surface.blit(n_txt, (tx, ty + 30))

        # Details
        det_off = ty + 110
        pygame.draw.line(surface, (40, 50, 40), (tx, det_off), (card.right - 40, det_off), 2)
        
        surface.blit(self.f_sub.render("RANK     : [ RECRUIT ]", True, (200, 200, 200)), (tx, det_off + 20))
        surface.blit(self.f_sub.render("UNIT     : BRVO-7", True, (200, 200, 200)), (tx, det_off + 50))
        surface.blit(self.f_sub.render("STATUS   : ACTIVE COMMAND", True, self.ACCENT), (tx, det_off + 80))

        self.btn_edit.draw(surface)
        self.btn_back.draw(surface)

    # Allow main.py to re-trigger image loading if the string updates manually (e.g. `ui.prof_screen.ins = res`)
    # To keep main.py compatibility untouched:
    @property
    def ins(self): return self.img_file
    @ins.setter
    def ins(self, val):
        if self.img_file != val:
            self.img_file = val
            self._load_image()
