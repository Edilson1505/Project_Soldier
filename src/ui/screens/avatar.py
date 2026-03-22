import pygame
import math
from ..elements.base import MenuButton
from ...core.paths import get_asset_path, get_safe_font

class AvatarSelection:
    def __init__(self):
        self.profiles = [
            {"id": "Mark",      "file": "Mark_profile_bg.jpg",       "label": "MARK"},
            {"id": "Jack",      "file": "jack_profile_bg.jpg",       "label": "JACK"},
            {"id": "WarMaster", "file": "war_master_profile_bg.jpg", "label": "WAR MASTER"}
        ]
        
        # Pre-load and scale images
        self.images = []
        for p in self.profiles:
            try:
                img = pygame.image.load(get_asset_path(p["file"])).convert()
                # Crop/scale to 140x140
                size = min(img.get_width(), img.get_height())
                rect = pygame.Rect((img.get_width() - size)//2, (img.get_height() - size)//2, size, size)
                cropped = img.subsurface(rect).copy()
                self.images.append(pygame.transform.scale(cropped, (140, 140)))
            except:
                default = pygame.Surface((140, 140))
                default.fill((40, 50, 45))
                pygame.draw.circle(default, (100, 120, 100), (70, 70), 50, 4)
                self.images.append(default)

        self.btn_save = MenuButton(0, 250, 320, 75, "CONFIRM ENTRY", is_right=False)
        self.selected = 0
        self.f_title = get_safe_font("Consolas", 60, bold=True)
        self.f_label = get_safe_font("Consolas", 20, bold=True)
        self.time = 0.0

    def update(self):
        self.time += 0.05
        sw_f, sh_f = pygame.display.get_surface().get_size()
        sw, sh = int(sw_f), int(sh_f)
        m_pos = pygame.mouse.get_pos() 
        m_down = pygame.mouse.get_pressed()[0]
        
        # Check clicks on profile cards
        spacing = 180
        start_x = sw//2 - (len(self.profiles) * spacing)//2 + (spacing//2)
        
        for i in range(len(self.profiles)):
            rect = pygame.Rect(start_x - 70 + i*spacing, sh//2 - 90, 140, 140)
            if rect.collidepoint(m_pos) and m_down: self.selected = i
            
        if self.btn_save.update(sw, sh):
            return self.profiles[self.selected]["file"]
        return None

    def draw(self, surface):
        surface.fill((8, 12, 10)) 
        sw_f, sh_f = surface.get_size()
        sw, sh = int(sw_f), int(sh_f)
        
        # Grid Background
        for x in range(0, sw, 80): pygame.draw.line(surface, (15, 20, 15), (x, 0), (x, sh))
        for y in range(0, sh, 80): pygame.draw.line(surface, (15, 20, 15), (0, y), (sw, y))
        
        # Title
        t_sha = self.f_title.render("OPERATOR SELECTION", True, (0,0,0))
        t = self.f_title.render("OPERATOR SELECTION", True, (240, 250, 240))
        surface.blit(t_sha, (sw//2 - t.get_width()//2 + 4, 100 + 4))
        surface.blit(t, (sw//2 - t.get_width()//2, 100))

        # Draw Cards
        spacing = 180
        start_x = sw//2 - (len(self.profiles) * spacing)//2 + (spacing//2)
        
        for i, (p, img) in enumerate(zip(self.profiles, self.images)):
            cx = start_x + i * spacing
            cy = sh//2 - 20
            rect = pygame.Rect(cx - 70, cy - 70, 140, 140)
            
            # Card highlight
            is_sel = (self.selected == i)
            c = (150, 200, 120) if is_sel else (50, 65, 50)
            
            # Image drop shadow
            pygame.draw.rect(surface, (0, 0, 0, 150), rect.move(8, 8), border_radius=6)
            
            # Draw Image
            img.set_alpha(255 if is_sel else 120)
            surface.blit(img, rect.topleft)
            
            # Border Frame
            pygame.draw.rect(surface, c, rect, 4 if is_sel else 2, border_radius=6)
            
            # Tech corner accents if selected
            if is_sel:
                ext = 10 + int(math.sin(self.time*4)*4)
                pygame.draw.lines(surface, c, False, [(rect.left-ext, rect.top+20), (rect.left-ext, rect.top-ext), (rect.left+20, rect.top-ext)], 4)
                pygame.draw.lines(surface, c, False, [(rect.right+ext, rect.bottom-20), (rect.right+ext, rect.bottom+ext), (rect.right-20, rect.bottom+ext)], 4)

            # Name Label
            l_col = (255, 255, 255) if is_sel else (120, 140, 120)
            name = self.f_label.render(p["label"], True, l_col)
            bg_rect = pygame.Rect(cx - name.get_width()//2 - 10, rect.bottom + 15, name.get_width() + 20, 30)
            pygame.draw.rect(surface, (0, 0, 0, 180), bg_rect, border_radius=4)
            pygame.draw.rect(surface, c, bg_rect, 1, border_radius=4)
            surface.blit(name, (bg_rect.x + 10, bg_rect.y + 5))

        self.btn_save.draw(surface)
