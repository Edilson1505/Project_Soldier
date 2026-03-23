import pygame
import math
from src.core.settings import MAX_AMMO, MAX_GRENADES, ROOM_W, ROOM_H, ROOMS_MAP
from src.core.paths import get_asset_path, get_safe_font

class TacticalHUD:
    def __init__(self, soldier):
        self.soldier = soldier
        self.time = 0.0
        self.kill_count = 0
        self._kill_anim = 0.0
        self._prev_kills = 0
        self.enemies_ref = []
        
        self.profile_name = "OPERATOR"
        self.profile_img_file = "Mark_profile_bg.jpg"
        self._prof_img = None
        self._prof_img_file_loaded = None

        # Authentic Military Terminal Fonts (Consolas)
        self.f_title = get_safe_font("Consolas", 28, bold=True)
        self.f_big   = get_safe_font("Consolas", 52, bold=True)
        self.f_med   = get_safe_font("Consolas", 24, bold=True)
        self.f_small = get_safe_font("Consolas", 15, bold=True)
        self.f_micro = get_safe_font("Consolas", 12, bold=True)
        
        # Military Palette
        self.TACTICAL_GREEN = (150, 200, 120)  
        self.MUTED_GREEN    = (80, 110, 70)    
        self.DARK_GREEN     = (10, 15, 12)     # Darker for contrast
        self.CRITICAL_RED   = (220, 40, 40)
        self.TEXT_BRIGHT    = (240, 250, 240)
        self.TEXT_MUTED     = (130, 160, 130)

        self.damage_vignette = None

    def _tactical_panel(self, surf, x, y, w, h, alpha=235):
        # AAA Military terminal panel
        pygame.draw.rect(surf, (0, 0, 0, 150), (x+6, y+6, w, h)) # Deeper shadow
        
        # Pure black base for highest legibility
        pygame.draw.rect(surf, (0, 0, 0), (x, y, w, h))

        bg = pygame.Surface((w, h), pygame.SRCALPHA)
        bg.fill((*self.DARK_GREEN, alpha))
        
        # Static grid
        for i in range(0, h, 4):
            pygame.draw.line(bg, (0, 0, 0, 80), (0, i), (w, i))
            
        # Animated Scanline Radar Effect
        scan_y = int((self.time * 60) % h)
        pygame.draw.line(bg, (150, 200, 120, 40), (0, scan_y), (w, scan_y), 4)
        pygame.draw.line(bg, (150, 200, 120, 90), (0, scan_y+1), (w, scan_y+1), 2)
        
        surf.blit(bg, (x, y))
        
        # Crisp borders
        pygame.draw.rect(surf, self.MUTED_GREEN, (x, y, w, h), 2)
        pygame.draw.line(surf, self.TACTICAL_GREEN, (x-1, y-1), (x+w//3, y-1), 4)
        pygame.draw.line(surf, self.TACTICAL_GREEN, (x-1, y-1), (x-1, y+h//3), 4)
        
        # Blinking tech corners
        if int(self.time * 4) % 2 == 0:
            pygame.draw.rect(surf, self.TACTICAL_GREEN, (x+w-10, y+h-10, 8, 8))

    def _draw_text_subtle_shadow(self, surf, text, font, color, pos):
        # 1px offset for clean military terminal shadow
        st = font.render(text, True, (0, 0, 0))
        surf.blit(st, (pos[0] + 1, pos[1] + 1))
        t = font.render(text, True, color)
        surf.blit(t, pos)

    def draw(self, surface, sw, sh, enemies=None):
        self.time += 0.05
        if enemies is not None: self.enemies_ref = enemies

        hp_pct = max(0, self.soldier.health / 100.0)

        # ── DAMAGE OVERLAY (Blood/Red Vignette) ─────────────────────────────
        if hp_pct < 0.35:
            if self.damage_vignette is None or self.damage_vignette.get_size() != (sw, sh):
                self.damage_vignette = pygame.Surface((sw, sh), pygame.SRCALPHA).convert_alpha()
                for i in range(0, sw, 16):
                    for j in range(0, sh, 16):
                        dx = (i - sw/2) / (sw/2)
                        dy = (j - sh/2) / (sh/2)
                        dist = (dx*dx + dy*dy) ** 0.5
                        if dist > 0.45:
                            alpha = int(min(120, (dist - 0.45) * 230))
                            pygame.draw.rect(self.damage_vignette, (255, 10, 0, alpha), (i, j, 16, 16))
            
            pulse = int(180 + 75 * math.sin(self.time * 8))
            tv = self.damage_vignette.copy()
            tv.fill((255, 255, 255, pulse), special_flags=pygame.BLEND_RGBA_MULT)
            surface.blit(tv, (0, 0))

        # Kill animation
        if self.kill_count != self._prev_kills:
            self._kill_anim = 1.0; self._prev_kills = self.kill_count
        self._kill_anim = max(0.0, self._kill_anim - 0.05)

        # Ensure image is loaded and scaled
        if self.profile_img_file != self._prof_img_file_loaded:
            self._prof_img_file_loaded = self.profile_img_file
            try:
                img = pygame.image.load(get_asset_path(self.profile_img_file)).convert()
                size = min(img.get_width(), img.get_height())
                rect = pygame.Rect((img.get_width() - size)//2, (img.get_height() - size)//2, size, size)
                cropped = img.subsurface(rect).copy()
                self._prof_img = pygame.transform.scale(cropped, (64, 64))
            except:
                self._prof_img = pygame.Surface((64, 64))
                self._prof_img.fill((20, 30, 25))

        # ── TOP-LEFT: Mission Identity & Profile ────────────────────────────────
        self._draw_text_subtle_shadow(surface, "PROJECT SOLDIER", self.f_title, self.TEXT_BRIGHT, (30, 30))
        self._draw_text_subtle_shadow(surface, "OP ZONE: SECTOR ALFA", self.f_micro, self.TACTICAL_GREEN, (30, 64))

        # Profile Frame
        prof_y = 90
        # Background shadow & panel
        pygame.draw.rect(surface, (0, 0, 0, 150), (36, prof_y + 6, 260, 80))
        pygame.draw.rect(surface, self.DARK_GREEN, (30, prof_y, 260, 80))
        pygame.draw.rect(surface, self.MUTED_GREEN, (30, prof_y, 260, 80), 2)
        
        # Profile Picture Thumbnail
        if self._prof_img:
            surface.blit(self._prof_img, (38, prof_y + 8))
        pygame.draw.rect(surface, self.TACTICAL_GREEN, (38, prof_y + 8, 64, 64), 2)
        
        # Name & Rank Display
        self._draw_text_subtle_shadow(surface, self.profile_name, self.f_med, self.TEXT_BRIGHT, (115, prof_y + 15))
        self._draw_text_subtle_shadow(surface, "RANK: RECRUIT", self.f_small, self.TEXT_MUTED, (115, prof_y + 45))

        # ── TOP-RIGHT: Tactical Feed ────────────────────────────────────────────
        pw, ph = 440, 230  # Very wide to ensure Spanish terms fit
        px, py = sw - pw - 30, 30 
        self._tactical_panel(surface, px, py, pw, ph)

        margin = 25
        curr_y = py + margin

        # VITAL SIGNS
        hp_color = self.TACTICAL_GREEN if hp_pct > 0.3 else self.CRITICAL_RED
        self._draw_text_subtle_shadow(surface, "COMBAT EFFECTIVENESS", self.f_small, self.TEXT_MUTED, (px + margin, curr_y))
        
        curr_y += 24
        hp_w, hp_h = pw - 50, 20
        pygame.draw.rect(surface, (15, 20, 15), (px + margin, curr_y, hp_w, hp_h))
        pygame.draw.rect(surface, (40, 50, 40), (px + margin, curr_y, hp_w, hp_h), 2)
        
        if hp_pct > 0:
            fill_rect = pygame.Rect(px + margin + 2, curr_y + 2, int((hp_w - 4) * hp_pct), hp_h - 4)
            pygame.draw.rect(surface, hp_color, fill_rect)
            # Pulse flash on low health
            if hp_pct < 0.3:
                glow_a = int(120 + 100 * math.sin(self.time * 10))
                glow = pygame.Surface(fill_rect.size, pygame.SRCALPHA)
                glow.fill((*self.CRITICAL_RED, glow_a))
                surface.blit(glow, fill_rect.topleft)
        
        hp_txt = f"{int(self.soldier.health)}%"
        hp_surf = self.f_micro.render(hp_txt, True, (0, 0, 0)) # Black text on green bar
        surface.blit(hp_surf, (px + margin + hp_w//2 - hp_surf.get_width()//2, curr_y + 3))

        curr_y += hp_h + 16
        pygame.draw.line(surface, self.MUTED_GREEN, (px+margin, curr_y), (px+pw-margin, curr_y), 2)
        curr_y += 16

        # AMMUNITION
        self._draw_text_subtle_shadow(surface, "AMMUNITION", self.f_small, self.TEXT_MUTED, (px + margin, curr_y))
        curr_y += 20
        ammo_txt = f"{self.soldier.ammo:02}"
        self._draw_text_subtle_shadow(surface, ammo_txt, self.f_big, self.TEXT_BRIGHT, (px + margin, curr_y - 6))
        
        # Military block ammo
        seg_w = (pw - 140) // MAX_AMMO
        seg_x, seg_y = px + margin + 80, curr_y + 12
        for i in range(MAX_AMMO):
            col = self.TACTICAL_GREEN if i < self.soldier.ammo else (35, 45, 35)
            pygame.draw.rect(surface, col, (seg_x + i * seg_w, seg_y, seg_w - 2, 18))

        curr_y += self.f_big.get_height() + 4
        self._draw_text_subtle_shadow(surface, "GRENADES:", self.f_small, self.TEXT_MUTED, (px + margin, curr_y))
        for i in range(MAX_GRENADES):
            g_col = self.TACTICAL_GREEN if i < self.soldier.grenades else (35, 45, 35)
            # Draw tiny tactical cylinders instead of circles
            pygame.draw.rect(surface, g_col, (px + 120 + i * 24, curr_y, 14, 16), border_radius=2)
            if i < self.soldier.grenades:
                pygame.draw.line(surface, (255, 255, 255), (px + 120 + i * 24 + 4, curr_y + 2), (px + 120 + i * 24 + 4, curr_y + 14), 2)

        # ── KILLS (Intel Panel) ────────────────────────────────────────────────
        kp_w, kp_h = 280, 85
        kp_x, kp_y = sw - kp_w - 30, py + ph + 20
        self._tactical_panel(surface, kp_x, kp_y, kp_w, kp_h)
        self._draw_text_subtle_shadow(surface, "HOSTILES KIA", self.f_small, self.TEXT_MUTED, (kp_x+15, kp_y+10))
        
        zoom = 1.0 + self._kill_anim * 0.4
        k_col = (255, 255, 255) if self._kill_anim > 0.1 else self.TEXT_BRIGHT
        kills = self.f_big.render(f"{self.kill_count:02}", True, k_col)
        if zoom > 1.0:
            nw, nh = int(kills.get_width()*zoom), int(kills.get_height()*zoom)
            kills = pygame.transform.scale(kills, (nw, nh))
        surface.blit(kills, (kp_x + kp_w//2 - kills.get_width()//2, kp_y + 30))

        # ── MINIMAP (Sat-Link) ─────────────────────────────────────────────────
        ms = 190
        mx, my = 35, prof_y + 120
        self._tactical_panel(surface, mx - 5, my - 25, ms + 10, ms + 30, alpha=235)
        self._draw_text_subtle_shadow(surface, "UAV UPLINK", self.f_small, self.TACTICAL_GREEN, (mx, my - 16))
        
        grid_cols = max(r[0] for r in ROOMS_MAP) + 1
        cw, ch = ms / grid_cols, ms / 2
        for r_col, r_row in ROOMS_MAP:
            rx = mx + r_col * cw
            ry = my + r_row * ch + (ms - ch) // 2
            pygame.draw.rect(surface, (12, 18, 14), (rx + 1, ry + 1, cw - 2, ch - 2))
            pygame.draw.rect(surface, self.MUTED_GREEN, (rx + 1, ry + 1, cw - 2, ch - 2), 1)

        # Player Blip (Crosshair style)
        p_col = int(self.soldier.x / ROOM_W)
        px_map = mx + p_col * cw + (self.soldier.x % ROOM_W) / ROOM_W * cw
        py_map = my + (ms - ch) // 2 + (self.soldier.y % ROOM_H) / ROOM_H * ch
        if int(self.time * 6) % 2 == 0:
            pygame.draw.line(surface, self.TEXT_BRIGHT, (px_map-5, py_map), (px_map+5, py_map), 2)
            pygame.draw.line(surface, self.TEXT_BRIGHT, (px_map, py_map-5), (px_map, py_map+5), 2)

        # Enemy blips (Red squares)
        for en in self.enemies_ref:
            if en.alive:
                e_col = int(en.x / ROOM_W)
                ex_map = mx + e_col * cw + (en.x % ROOM_W) / ROOM_W * cw
                ey_map = my + (ms - ch) // 2 + (en.y % ROOM_H) / ROOM_H * ch
                pygame.draw.rect(surface, self.CRITICAL_RED, (ex_map-3, ey_map-3, 6, 6))
