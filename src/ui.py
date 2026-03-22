import pygame
import math
import random
from .settings import MAX_AMMO, MAX_GRENADES, ROOMS_MAP, ROOM_W, ROOM_H, SCREEN_W, SCREEN_H

class AmbientParticle:
    def __init__(self, sw, sh):
        self.x = random.uniform(0, sw) ; self.y = random.uniform(0, sh)
        self.vx = random.uniform(-0.5, 0.5) ; self.vy = random.uniform(-0.2, -0.8)
        self.life = random.uniform(100, 255) ; self.size = random.uniform(1, 4)
    def update(self):
        self.x += self.vx ; self.y += self.vy ; self.life -= 0.5
        return self.life > 0
    def draw(self, surface):
        s = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (150, 200, 255, int(self.life//2.5)), (self.size, self.size), self.size)
        surface.blit(s, (self.x, self.y))

class UIParticle:
    def __init__(self, x, y):
        self.x, self.y = x, y ; angle = random.uniform(0, math.pi * 2) ; speed = random.uniform(2, 6)
        self.vx, self.vy = math.cos(angle) * speed, math.sin(angle) * speed ; self.life = 255
    def update(self):
        self.x += self.vx ; self.y += self.vy ; self.life -= 20
        return self.life > 0
    def draw(self, surface):
        s = pygame.Surface((3, 3), pygame.SRCALPHA) ; s.fill((255, 255, 255, self.life)) ; surface.blit(s, (self.x, self.y))

class MenuButton:
    def __init__(self, rx_p, ry_p, w, h, text, is_right=True, small=False):
        self.rx_p, self.ry_p = rx_p, ry_p ; self.w, self.h = w, h ; self.text = text
        self.is_right = is_right ; self.rect = pygame.Rect(0, 0, w, h)
        self.f = pygame.font.SysFont("Impact", 20 if small else 32)
        self.hover = self.pressed = self.last_m = False ; self.y_off = 0.0

    def update(self, sw, sh):
        if self.is_right: cx = sw - self.rx_p ; cy = sh // 2 + self.ry_p
        else: cx = sw // 2 + self.rx_p ; cy = sh // 2 + self.ry_p
        self.rect.center = (cx, cy)
        m = pygame.mouse.get_pos() ; self.hover = self.rect.collidepoint(m)
        md = pygame.mouse.get_pressed()[0] ; c = self.hover and md and not self.last_m
        self.pressed, self.last_m = self.hover and md, md 
        self.y_off += ((8 if self.pressed else 0) - self.y_off) * 0.4
        return c

    def draw(self, surface):
        r = self.rect.copy() ; r.y += int(self.y_off)
        c = (45, 55, 80) if self.hover else (25, 28, 40)
        pygame.draw.rect(surface, (150, 180, 255, 180), r, border_radius=4)
        pygame.draw.rect(surface, c, r.inflate(-4, -4), border_radius=2)
        if self.hover:
            ext = 8 ; cl = (180, 220, 255)
            pygame.draw.lines(surface, cl, False, [(r.left-ext, r.top+15), (r.left-ext, r.top-ext), (r.left+15, r.top-ext)], 2)
            pygame.draw.lines(surface, cl, False, [(r.right+ext, r.bottom-15), (r.right+ext, r.bottom+ext), (r.right-15, r.bottom+ext)], 2)
        t = self.f.render(self.text, True, (255, 255, 255))
        surface.blit(t, (r.centerx - t.get_width()//2, r.centery - t.get_height()//2))

class TextInput:
    def __init__(self, ry_p, w, h, label):
        self.ry_p, self.w, self.h = ry_p, w, h ; self.text = "" ; self.label = label
        self.f = pygame.font.SysFont("Consolas", 28, bold=True) ; self.active = False ; self.rect = pygame.Rect(0,0,w,h)
    def update(self, events, sw, sh):
        self.rect.center = (sw // 2, sh // 2 + self.ry_p)
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN: self.active = self.rect.collidepoint(event.pos)
            if self.active and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE: self.text = self.text[:-1]
                elif len(self.text) < 12 and event.unicode.isprintable(): self.text += event.unicode
    def draw(self, surface):
        c = (150, 180, 255) if self.active else (40, 45, 60)
        pygame.draw.rect(surface, (10, 14, 25, 220), self.rect, border_radius=5)
        pygame.draw.rect(surface, c, self.rect, 2, border_radius=5)
        l_txt = pygame.font.SysFont("Impact", 20).render(self.label, True, (150, 180, 255))
        surface.blit(l_txt, (self.rect.x, self.rect.y - 32))
        txt_s = self.f.render(self.text + ("_" if self.active and (pygame.time.get_ticks()//500 % 2) else ""), True, (255, 255, 255))
        surface.blit(txt_s, (self.rect.x + 15, self.rect.y + (self.rect.h - txt_s.get_height())//2))

class LoginMenu:
    def __init__(self):
        try: self.bg = pygame.image.load("login_portait_bg.png").convert_alpha()
        except: self.bg = None
        self.name_in = TextInput(20, 500, 75, "CALIBRACIÓN DE IDENTIDAD (Nombre)")
        self.btn = MenuButton(0, 140, 350, 75, "DESBLOQUEAR ACCESO", is_right=False)
        self.t_font = pygame.font.SysFont("Impact", 80) ; self.time = 0.0
        self.ambient = [AmbientParticle(SCREEN_W, SCREEN_H) for _ in range(80)]

    def update(self, events):
        sw, sh = pygame.display.get_surface().get_size() ; self.time += 0.05
        self.ambient = [p for p in self.ambient if p.update()]
        if len(self.ambient) < 100: self.ambient.append(AmbientParticle(sw, sh))
        self.name_in.update(events, sw, sh)
        if self.btn.update(sw, sh): return "login"
        return None

    def draw(self, surface):
        sw, sh = surface.get_size() ; surface.fill((3, 5, 12))
        if self.bg:
            ox = math.sin(self.time) * 10 ; bh = sh + 40
            bw = int(self.bg.get_width() * (bh / self.bg.get_height()))
            surface.blit(pygame.transform.scale(self.bg, (bw, bh)), (-20 + ox, -20))
            overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
            overlay.fill((5, 10, 25, 140)) ; surface.blit(overlay, (0, 0))
        for p in self.ambient: p.draw(surface)
        t1 = self.t_font.render("SISTEMA DE SEGURIDAD", True, (200, 220, 255))
        surface.blit(t1, (sw//2 - t1.get_width()//2, sh//2 - 280))
        t2 = self.t_font.render("¡ACCESO RESTRINGIDO!", True, (255, 80, 80))
        surface.blit(t2, (sw//2 - t2.get_width()//2, sh//2 - 180))
        self.name_in.draw(surface) ; self.btn.draw(surface)

class MainMenu:
    def __init__(self):
        try: self.bg = pygame.image.load("main_portait_bg.png").convert_alpha()
        except: self.bg = None
        self.title_f = pygame.font.SysFont("Impact", 100)
        self.btns = {
            "solo": MenuButton(240, -60, 420, 80, "INICIAR OPERACIÓN"),
            "lan":  MenuButton(240, 60, 420, 80, "SISTEMA LAN"),
            "prof": MenuButton(240, 180, 420, 80, "PERFIL DE OPERADOR"),
            "exit": MenuButton(240, 300, 180, 60, "SALIR", small=True)
        }
        self.time = 0.0

    def update(self):
        sw, sh = pygame.display.get_surface().get_size() ; self.time += 0.02
        actions = []
        for name, btn in self.btns.items():
            if btn.update(sw, sh): actions.append(name)
        return actions

    def draw(self, surface):
        sw, sh = surface.get_size() ; surface.fill((5, 5, 12))
        if self.bg:
            ox = math.sin(self.time) * 15 ; bh = sh + 40
            bw = int(self.bg.get_width() * (bh / self.bg.get_height()))
            surface.blit(pygame.transform.scale(self.bg, (bw, bh)), (-20 + ox, -20))
            
            # 🌑 MEZCLA DE SOMBRA TÁCTICA (Gradiente Profundo 800px)
            # Dibujamos de derecha a izquierda un gradiente de opacidad
            sh_width = 800
            for i in range(sh_width):
                alpha = int((i/sh_width) * 255)
                sh_line = pygame.Surface((3, sh), pygame.SRCALPHA)
                sh_line.fill((5, 5, 12, alpha))
                surface.blit(sh_line, (sw - sh_width + i, 0))
        
        # Panel base sólido (Derecha)
        pygame.draw.rect(surface, (5, 5, 12), (sw - 400, 0, 400, sh))
        
        t = self.title_f.render("PROYECTO", True, (255, 255, 255))
        s = self.title_f.render("SOLDADO", True, (150, 180, 255))
        surface.blit(t, (sw - 240 - t.get_width()//2, 100))
        surface.blit(s, (sw - 240 - s.get_width()//2, 200))
        for btn in self.btns.values(): btn.draw(surface)

class ProfileScreen:
    def __init__(self, username, icon_data):
        self.user = username ; self.ins = icon_data
        self.btn_edit = MenuButton(0, 180, 400, 75, "CAMBIAR AVATAR", is_right=False)
        self.btn_back = MenuButton(0, 280, 200, 60, "VOLVER", is_right=False, small=True)
        self.f_big = pygame.font.SysFont("Impact", 60)
        self.f_sub = pygame.font.SysFont("Consolas", 22, bold=True)

    def update(self):
        sw, sh = pygame.display.get_surface().get_size()
        if self.btn_edit.update(sw, sh): return "edit"
        if self.btn_back.update(sw, sh): return "back"
        return None

    def draw(self, surface):
        surface.fill((8, 8, 12)) ; sw, sh = surface.get_size()
        card = pygame.Rect(sw//2 - 350, sh//2 - 250, 700, 350)
        pygame.draw.rect(surface, (20, 25, 45), card, border_radius=15)
        pygame.draw.rect(surface, (150, 180, 255, 100), card, 2, border_radius=15)
        av_rect = pygame.Rect(card.x + 50, card.y + 50, 200, 200)
        pygame.draw.rect(surface, (10, 15, 30), av_rect, border_radius=10)
        pygame.draw.rect(surface, self.ins["color"], av_rect, 3, border_radius=10)
        cx, cy = av_rect.center ; c = self.ins["color"]
        if self.ins["shape"] == "circle": pygame.draw.circle(surface, c, (cx, cy), 60, 4)
        elif self.ins["shape"] == "cross": 
            pygame.draw.line(surface, c, (cx-50, cy), (cx+50, cy), 8)
            pygame.draw.line(surface, c, (cx, cy-50), (cx, cy+50), 8)
        elif self.ins["shape"] == "target":
            pygame.draw.circle(surface, c, (cx, cy), 60, 2) ; pygame.draw.circle(surface, (255, 255, 255), (cx, cy), 10)
        elif self.ins["shape"] == "hex":
            pygame.draw.polygon(surface, c, [(cx, cy-60), (cx+52, cy-30), (cx+52, cy+30), (cx, cy+60), (cx-52, cy+30), (cx-52, cy-30)], 4)
        surface.blit(self.f_sub.render("FICHA DE OPERADOR", True, (100, 150, 255)), (card.x + 300, card.y + 60))
        surface.blit(self.f_big.render(self.user.upper(), True, (255, 255, 255)), (card.x + 300, card.y + 90))
        surface.blit(self.f_sub.render(f"RANGO: [ RECLUTA ]", True, (150, 255, 150)), (card.x + 300, card.y + 180))
        surface.blit(self.f_sub.render(f"INSIGNIA: {self.ins['name']}", True, (200, 200, 240)), (card.x + 300, card.y + 220))
        self.btn_edit.draw(surface) ; self.btn_back.draw(surface)

class AvatarSelection:
    def __init__(self):
        self.insignias = [
            {"name": "ALFA",  "color": (80, 120, 255), "shape": "circle"},
            {"name": "BRAVO",  "color": (80, 255, 120), "shape": "cross"},
            {"name": "FANTASMA",  "color": (255, 80, 100), "shape": "target"},
            {"name": "IMPACTO", "color": (240, 240, 80), "shape": "hex"}
        ]
        self.btn_save = MenuButton(0, 250, 300, 75, "CONFIRMAR", is_right=False)
        self.selected = 0 ; self.f_title = pygame.font.SysFont("Impact", 60)

    def update(self):
        sw, sh = pygame.display.get_surface().get_size()
        m_pos = pygame.mouse.get_pos() ; m_down = pygame.mouse.get_pressed()[0]
        for i in range(4):
            rect = pygame.Rect(sw//2 - 200 + i*110, sh//2 - 50, 100, 100)
            if rect.collidepoint(m_pos) and m_down: self.selected = i
        if self.btn_save.update(sw, sh): return "save"
        return None

    def draw(self, surface):
        surface.fill((5, 5, 10)) ; sw, sh = surface.get_size()
        t = self.f_title.render("SELECCIÓN DE INSIGNIA", True, (255, 255, 255))
        surface.blit(t, (sw//2 - t.get_width()//2, 100))
        for i, ins in enumerate(self.insignias):
            rect = pygame.Rect(sw//2 - 200 + i*110, sh//2 - 50, 100, 100)
            c = ins["color"] if self.selected == i else (50, 55, 70)
            pygame.draw.rect(surface, (10, 10, 20), rect, border_radius=10)
            pygame.draw.rect(surface, c, rect, 3 if self.selected == i else 1, border_radius=10)
            cx, cy = rect.center
            if ins["shape"] == "circle": pygame.draw.circle(surface, c, (cx, cy), 25, 3)
            elif ins["shape"] == "cross": 
                pygame.draw.line(surface, c, (cx-20, cy), (cx+20, cy), 5)
                pygame.draw.line(surface, c, (cx, cy-20), (cx, cy+20), 5)
            elif ins["shape"] == "target":
                pygame.draw.circle(surface, c, (cx, cy), 25, 2) ; pygame.draw.circle(surface, (255, 255, 255), (cx, cy), 4)
            elif ins["shape"] == "hex":
                pygame.draw.polygon(surface, c, [(cx, cy-25), (cx+22, cy-12), (cx+22, cy+12), (cx, cy+25), (cx-22, cy+12), (cx-22, cy-12)], 3)
            name = pygame.font.SysFont("Impact", 18).render(ins["name"], True, c)
            surface.blit(name, (rect.centerx - name.get_width()//2, rect.bottom + 10))
        self.btn_save.draw(surface)

class LANMenu:
    def __init__(self):
        self.title_f = pygame.font.SysFont("Impact", 60)
        self.btns = {
            "create": MenuButton(0, -50, 450, 85, "CREAR SALA TÁCTICA", is_right=False),
            "join":   MenuButton(0, 50, 450, 85, "BUSCAR Y UNIRSE", is_right=False),
            "back":   MenuButton(0, 200, 220, 65, "VOLVER", is_right=False, small=True)
        }

    def update(self):
        sw, sh = pygame.display.get_surface().get_size()
        actions = []
        for name, btn in self.btns.items():
            if btn.update(sw, sh): actions.append(name)
        return actions

    def draw(self, surface):
        sw, sh = surface.get_size() ; surface.fill((5, 8, 15))
        pygame.draw.rect(surface, (100, 150, 255, 30), (50, 50, 320, sh-100), border_radius=15)
        t_txt = self.title_f.render("SISTEMA DE RED LOCAL", True, (255, 255, 255))
        surface.blit(t_txt, (sw//2 - t_txt.get_width()//2, 100))
        for btn in self.btns.values(): btn.draw(surface)

class TacticalHUD:
    def __init__(self, soldier):
        self.soldier = soldier ; self.radar_sz = 180 ; self.hp_w = 260
        self.a_f = pygame.font.SysFont("Impact", 48) ; self.s_f = pygame.font.SysFont("Consolas", 20, bold=True)
    def draw(self, surface, sw, sh):
        rx, ry = 30, 30 ; pygame.draw.rect(surface, (0, 0, 0, 200), (rx, ry, self.radar_sz, self.radar_sz), border_radius=10)
        pygame.draw.rect(surface, (100, 100, 140), (rx, ry, self.radar_sz, self.radar_sz), 2, border_radius=10)
        co = self.radar_sz // 2 - 20 ; from .settings import ROOMS_MAP, ROOM_W, ROOM_H
        for rrx, rry in ROOMS_MAP: pygame.draw.rect(surface, (50, 50, 70), (rx + co + rrx*22, ry + co + rry*22, 18, 18), border_radius=2)
        px = rx + co + (self.soldier.x / ROOM_W) * 22 + 9; py = ry + co + (self.soldier.y / ROOM_H) * 22 + 9
        if (pygame.time.get_ticks() // 250) % 2 == 0: pygame.draw.circle(surface, (255, 255, 255), (int(px), int(py)), 5)
        hx, hy = rx + self.radar_sz + 30, ry + 10
        pygame.draw.rect(surface, (30, 30, 45), (hx, hy, self.hp_w, 25), border_radius=5)
        pygame.draw.rect(surface, (120, 255, 120), (hx + 3, hy + 3, (self.hp_w-6), 19), border_radius=3)
        surface.blit(self.s_f.render("ESTADO: OPERATIVO", True, (255, 255, 255)), (hx, hy + 35))
        ax, ay = sw - 360, 30 ; pygame.draw.rect(surface, (0, 0, 0, 180), (ax, ay, 330, 120), border_radius=15)
        surface.blit(self.a_f.render(f"BALAS: {self.soldier.ammo:02}", True, (255, 255, 255)), (ax+30, ay+15))
        surface.blit(self.s_f.render(f"GRANADAS: {self.soldier.grenades}", True, (200, 255, 200)), (ax+30, ay+80))

class PauseMenu:
    def __init__(self):
        self.r_btn = MenuButton(0, -60, 420, 80, "REANUDAR OPERACIÓN", is_right=False)
        self.q_btn = MenuButton(0, 60, 420, 80, "MENU PRINCIPAL", is_right=False)
    def update(self, sw, sh):
        if self.r_btn.update(sw, sh): return "resume"
        if self.q_btn.update(sw, sh): return "quit"
        return None
    def draw(self, surface):
        sw, sh = surface.get_size() ; ov = pygame.Surface((sw, sh), pygame.SRCALPHA); ov.fill((0, 0, 0, 180)); surface.blit(ov, (0, 0))
        self.r_btn.draw(surface); self.q_btn.draw(surface)

class GameUI:
    def __init__(self, soldier):
        self.soldier = soldier ; self.particles = [] ; self.hud = TacticalHUD(soldier)
        self.p_menu = PauseMenu() ; self.login_menu = LoginMenu() ; self.main_menu = MainMenu()
        self.lan_menu = LANMenu() ; self.avatar_sel = AvatarSelection() ; self.prof_screen = None
        self.buttons = { "shoot": UIButton(2, 2, -150, -150, 80, "shoot"), "grenade": UIButton(2, 2, -180, -320, 45, "grenade"),
                         "reload": UIButton(2, 2, -320, -180, 45, "reload"), "pause": UIButton(1, 0, 0, 55, 30, "pause") }

    def update_login(self, evs): return self.login_menu.update(evs)
    def update_main(self): return self.main_menu.update()
    def update_lan(self): return self.lan_menu.update()
    def update_prof(self): return self.prof_screen.update()
    def update_avatar(self): return self.avatar_sel.update()
    def draw_login(self, s): self.login_menu.draw(s)
    def draw_main(self, s): self.main_menu.draw(s)
    def draw_lan(self, s): self.lan_menu.draw(s)
    def draw_prof(self, s): self.prof_screen.draw(s)
    def draw_avatar(self, s): self.avatar_sel.draw(s)
    def update(self, is_paused):
        sw, sh = pygame.display.get_surface().get_size() ; self.particles = [p for p in self.particles if p.update()]
        if is_paused: return self.p_menu.update(sw, sh)
        actions = []
        for name, btn in self.buttons.items():
            if btn.update(sw, sh, self.particles): actions.append(name)
        return actions
    def draw(self, surface, is_paused):
        sw, sh = surface.get_size()
        if is_paused: self.p_menu.draw(surface); return
        self.hud.draw(surface, sw, sh)
        for b in self.buttons.values(): b.draw(surface)
        for p in self.particles: p.draw(surface)

class UIButton:
    def __init__(self, ax, ay, rx, ry, radius, icon_type):
        self.ax, self.ay, self.rx, self.ry = ax, ay, rx, ry
        self.base_r = radius ; self.icon_type = icon_type; self.cx = self.cy = 0; self.scale = 1.0; self.pressed = self.last_m = False
    def update(self, sw, sh, p):
        if self.ax == 0: self.cx = self.rx
        elif self.ax == 1: self.cx = sw // 2 + self.rx
        else: self.cx = sw + self.rx
        if self.ay == 0: self.cy = self.ry
        elif self.ay == 1: self.cy = sh // 2 + self.ry
        else: self.cy = sh + self.ry
        m = pygame.mouse.get_pos() ; dist = math.hypot(m[0] - self.cx, m[1] - self.cy)
        h = dist < self.base_r ; md = pygame.mouse.get_pressed()[0]
        c = h and md and not self.last_m ; self.pressed, self.last_m = h and md, md
        if c: [p.append(UIParticle(self.cx, self.cy)) for _ in range(10)]
        self.scale += ((1.2 if h and not self.pressed else 1.0) - self.scale) * 0.2
        return c
    def draw(self, surface):
        r = int(self.base_r * self.scale)
        pygame.draw.circle(surface, (60, 60, 75), (self.cx, self.cy), r)
        pygame.draw.circle(surface, (220, 220, 240), (self.cx, self.cy), r, 2)
        self._icon(surface, self.cx, self.cy, r)
    def _icon(self, surface, cx, cy, r):
        s = int(r*0.4); c = (255, 255, 255)
        if self.icon_type=="shoot": pygame.draw.circle(surface,c,(cx,cy),s,2); pygame.draw.circle(surface,c,(cx,cy),4)
        elif self.icon_type=="grenade": pygame.draw.circle(surface,c,(cx,cy+5),s//2); pygame.draw.rect(surface,c,(cx-3,cy-s,6,10))
        elif self.icon_type=="reload": pygame.draw.arc(surface,c,(cx-s,cy-s,s*2,s*2),0.5,5.5,3)
        elif self.icon_type=="pause": pygame.draw.rect(surface,c,(cx-8,cy-s,6,s*2)); pygame.draw.rect(surface,c,(cx+2,cy-s,6,s*2))
