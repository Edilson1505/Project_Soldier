import pygame
import math
import random
from src.core.paths import get_safe_font

class AmbientParticle:
    def __init__(self, sw, sh):
        self.x, self.y = random.uniform(0, sw), random.uniform(0, sh)
        self.vx, self.vy = random.uniform(-0.4, 0.4), random.uniform(-0.2, -0.6)
        self.life = random.uniform(80, 200)
        self.size = random.uniform(1, 4)
    def update(self):
        self.x += self.vx; self.y += self.vy; self.life -= 1.0
        return self.life > 0
    def draw(self, surface):
        if self.life < 0: return
        s = pygame.Surface((int(self.size*2), int(self.size*2)), pygame.SRCALPHA)
        pygame.draw.circle(s, (150, 200, 255, int(self.life//1.8)), (int(self.size), int(self.size)), int(self.size))
        surface.blit(s, (self.x, self.y))

class UIParticle:
    def __init__(self, x, y):
        self.x, self.y = x, y
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(3, 8)
        self.vx, self.vy = math.cos(angle) * speed, math.sin(angle) * speed
        self.life = 255
    def update(self):
        self.x += self.vx; self.y += self.vy; self.life -= 25
        return self.life > 0
    def draw(self, surface):
        if self.life <= 0: return
        # Glowing horizontal sparks instead of tiny dots
        s = pygame.Surface((12, 4), pygame.SRCALPHA)
        s.fill((255, 200, 100, int(self.life)))
        angle = math.degrees(math.atan2(self.vy, self.vx))
        rot_s = pygame.transform.rotate(s, -angle)
        surface.blit(rot_s, (self.x - rot_s.get_width()//2, self.y - rot_s.get_height()//2))

class MenuButton:
    def __init__(self, rx_p, ry_p, w, h, text, is_right=True, small=False):
        self.rx_p, self.ry_p = rx_p, ry_p
        self.w, self.h = w, h
        self.text = text
        self.is_right = is_right
        self.rect = pygame.Rect(0, 0, w, h)
        # Consolas military terminal look
        self.f_size = 28 if small else 38
        self.f = get_safe_font("Consolas", self.f_size, bold=True)
        self.hover = self.pressed = self.last_m = False
        self.y_off = 0.0
        self.hover_scale = 0.0

    def update(self, sw, sh):
        cx = sw - self.rx_p if self.is_right else sw // 2 + self.rx_p
        cy = sh // 2 + self.ry_p
        self.rect.center = (cx, cy)
        m = pygame.mouse.get_pos()
        self.hover = self.rect.collidepoint(m)
        md = pygame.mouse.get_pressed()[0]
        c = self.hover and md and not self.last_m
        self.pressed, self.last_m = self.hover and md, md 
        
        self.y_off += ((6 if self.pressed else 0) - self.y_off) * 0.4
        self.hover_scale += ((1.0 if self.hover else 0.0) - self.hover_scale) * 0.2
        return c

    def draw(self, surface):
        r = self.rect.copy()
        r.y += int(self.y_off)
        
        # Drop Shadow
        shadow_rect = r.copy()
        shadow_rect.y += 6; shadow_rect.x += 6
        pygame.draw.rect(surface, (0, 0, 0, 120), shadow_rect, border_radius=4)

        bg_col = (45, 60, 45) if self.hover else (22, 28, 24)
        pygame.draw.rect(surface, bg_col, r, border_radius=4)
        
        pygame.draw.line(surface, (100, 130, 100), r.topleft, r.topright, 2)
        pygame.draw.line(surface, (100, 130, 100), r.topleft, r.bottomleft, 2)
        pygame.draw.line(surface, (10, 15, 12), r.bottomleft, r.bottomright, 3)
        pygame.draw.line(surface, (10, 15, 12), r.topright, r.bottomright, 3)

        # Tech Accent lines
        if self.hover_scale > 0.05:
            ext = int(14 * self.hover_scale)
            cl = (150, 200, 120)
            pygame.draw.lines(surface, cl, False, [(r.left-ext, r.top+20), (r.left-ext, r.top-ext), (r.left+20, r.top-ext)], 3)
            pygame.draw.lines(surface, cl, False, [(r.right+ext, r.bottom-20), (r.right+ext, r.bottom+ext), (r.right-20, r.bottom+ext)], 3)

        txt_col = (255, 255, 255) if not self.hover else (180, 220, 150)
        t = self.f.render(self.text, True, txt_col)
        ts = self.f.render(self.text, True, (0, 0, 0))
        tx, ty = r.centerx - t.get_width()//2, r.centery - t.get_height()//2
        surface.blit(ts, (tx + 2, ty + 2))
        surface.blit(t, (tx, ty))


class TextInput:
    def __init__(self, ry_p, w, h, label):
        self.ry_p, self.w, self.h = ry_p, w, h
        self.text = ""
        self.label = label
        self.f = get_safe_font("Consolas", 32, bold=True)
        self.l_f = get_safe_font("Consolas", 20, bold=True)
        self.active = False
        self.rect = pygame.Rect(0,0,w,h)

    def update(self, events, sw, sh):
        self.rect.center = (sw // 2, sh // 2 + self.ry_p)
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN: 
                self.active = self.rect.collidepoint(event.pos)
            if self.active and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE: self.text = self.text[:-1]
                elif len(self.text) < 14 and event.unicode.isprintable(): self.text += event.unicode

    def draw(self, surface):
        pygame.draw.rect(surface, (0, 0, 0, 150), self.rect.move(4, 4), border_radius=4)
        
        bg_col = (15, 20, 18) if self.active else (10, 14, 12)
        pygame.draw.rect(surface, bg_col, self.rect, border_radius=4)
        
        # Inner Bevel
        pygame.draw.line(surface, (5, 8, 5), self.rect.topleft, self.rect.topright, 2)
        pygame.draw.line(surface, (5, 8, 5), self.rect.topleft, self.rect.bottomleft, 2)
        pygame.draw.line(surface, (40, 50, 45), self.rect.bottomleft, self.rect.bottomright, 2)
        pygame.draw.line(surface, (40, 50, 45), self.rect.topright, self.rect.bottomright, 2)

        if self.active: pygame.draw.rect(surface, (150, 200, 120), self.rect, 2, border_radius=4)

        l_s = self.l_f.render(self.label, True, (0,0,0))
        l_txt = self.l_f.render(self.label, True, (130, 150, 130) if not self.active else (150, 200, 120))
        surface.blit(l_s, (self.rect.x + 2, self.rect.y - 32))
        surface.blit(l_txt, (self.rect.x, self.rect.y - 34))

        disp_txt = self.text + ("_" if self.active and (pygame.time.get_ticks()//300 % 2) else "")
        txt_s = self.f.render(disp_txt, True, (240, 250, 240))
        surface.blit(txt_s, (self.rect.x + 15, self.rect.y + (self.rect.h - txt_s.get_height())//2))


class UIButton:
    def __init__(self, ax, ay, rx, ry, radius, icon_type):
        self.ax, self.ay, self.rx, self.ry = ax, ay, rx, ry
        self.base_r = radius; self.icon_type = icon_type; self.cx = self.cy = 0; self.scale = 1.0
        self.pressed = self.last_m = False
        self.rot_angle = 0.0

    def update(self, sw, sh, p):
        if self.ax == 0: self.cx = self.rx
        elif self.ax == 1: self.cx = sw // 2 + self.rx
        else: self.cx = sw + self.rx
        if self.ay == 0: self.cy = self.ry
        elif self.ay == 1: self.cy = sh // 2 + self.ry
        else: self.cy = sh + self.ry
        
        m = pygame.mouse.get_pos(); dist = math.hypot(m[0] - self.cx, m[1] - self.cy)
        h = dist < self.base_r; md = pygame.mouse.get_pressed()[0]
        c = h and md and not self.last_m; self.pressed, self.last_m = h and md, md
        
        # Intense particles on action
        if c: [p.append(UIParticle(self.cx, self.cy)) for _ in range(15)]
        
        self.scale += ((1.15 if h and not self.pressed else 0.85 if self.pressed else 1.0) - self.scale) * 0.3
        self.rot_angle += 2.0 if h else 0.5
        return c

    def draw(self, surface):
        r = int(self.base_r * self.scale)
        
        # Deep Drop Shadow
        pygame.draw.circle(surface, (0, 0, 0, 180), (self.cx + 6, self.cy + 6), r)

        # 3D Base Platform
        is_toggled = getattr(self, "is_toggled", False)
        bg = (50, 60, 50) if self.pressed or is_toggled else (30, 40, 35)
        pygame.draw.circle(surface, bg, (self.cx, self.cy), r)
        
        # High-tech Rotating Border Overlay
        overlay = pygame.Surface((r*2+4, r*2+4), pygame.SRCALPHA)
        center = (r+2, r+2)
        # Base ring
        pygame.draw.circle(overlay, (80, 100, 80, 200), center, r, 4)
        # Tech dashes
        for i in range(4):
            math_ang = math.radians(self.rot_angle + i * 90)
            ex = center[0] + math.cos(math_ang) * r
            ey = center[1] + math.sin(math_ang) * r
            pygame.draw.circle(overlay, (150, 200, 120), (int(ex), int(ey)), 4)
            
        surface.blit(overlay, (self.cx - r - 2, self.cy - r - 2))

        # Inner glow when pressed or toggled
        if self.pressed or is_toggled:
            pygame.draw.circle(surface, (150, 200, 120, 80), (self.cx, self.cy), int(r*0.8))

        # Detailed Military Icons
        s = int(r*0.45); c = (240, 250, 240) if not self.pressed and not is_toggled else (255, 255, 255)
        
        if self.icon_type == "shoot": 
            # Crosshair
            pygame.draw.circle(surface, c, (self.cx, self.cy), s, 3)
            pygame.draw.line(surface, c, (self.cx, self.cy-s-6), (self.cx, self.cy-s+4), 3)
            pygame.draw.line(surface, c, (self.cx, self.cy+s-4), (self.cx, self.cy+s+6), 3)
            pygame.draw.line(surface, c, (self.cx-s-6, self.cy), (self.cx-s+4, self.cy), 3)
            pygame.draw.line(surface, c, (self.cx+s-4, self.cy), (self.cx+s+6, self.cy), 3)
            pygame.draw.circle(surface, (255, 40, 40), (self.cx, self.cy), 4) # Red dot sight
            
        elif self.icon_type == "grenade": 
            # Detailed Frag Grenade
            gx, gy = self.cx, self.cy+4
            pygame.draw.circle(surface, c, (gx, gy), s//2 + 2)
            pygame.draw.rect(surface, c, (gx-5, gy-s-2, 10, 14)) # fuse base
            pygame.draw.line(surface, c, (gx+5, gy-s-4), (gx+12, gy-s+4), 3) # spoon lever
            pygame.draw.circle(surface, c, (gx-8, gy-s-2), 3) # pin ring
            
        elif self.icon_type == "reload": 
            # Tactical Reload Arrows
            pygame.draw.arc(surface, c, (self.cx-s, self.cy-s, s*2, s*2), 0.5, 5.0, 4)
            # Arrow head
            ax = self.cx + math.cos(0.5)*s
            ay = self.cy - math.sin(0.5)*s
            pygame.draw.polygon(surface, c, [(ax, ay-6), (ax+8, ay+6), (ax-8, ay+6)])
            
        elif self.icon_type == "run":
            # Tactical Sprint (Triple Fast-Forward Chevrons)
            for i in range(3):
                y_off = self.cy - s + i*9 + 4
                pygame.draw.lines(surface, c, False, [(self.cx-10, y_off+6), (self.cx, y_off-4), (self.cx+10, y_off+6)], 3)
            
        elif self.icon_type == "pause": 
            # Sturdy Pause Bars
            pygame.draw.rect(surface, c, (self.cx-12, self.cy-s, 8, s*2), border_radius=2)
            pygame.draw.rect(surface, c, (self.cx+4, self.cy-s, 8, s*2), border_radius=2)
