import pygame
import math

class VirtualJoystick:
    def __init__(self, x, y, radius=60, stick_radius=25):
        self.base_x = x
        self.base_y = y
        self.x = x
        self.y = y
        self.radius = radius
        self.stick_radius = stick_radius
        self.active = False
        self.dx = 0.0
        self.dy = 0.0
        
        # Epic Styles
        self.base_color = (15, 20, 30, 160)
        self.border_color = (80, 150, 200, 200)
        self.stick_color = (150, 220, 255, 220)
        self.pulse = 0.0
        self.ring_rot = 0.0

    def process_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                if math.hypot(mx - self.base_x, my - self.base_y) <= self.radius * 1.5:
                    self.active = True
                    self.update_stick(mx, my)
            elif event.type == pygame.MOUSEMOTION and self.active:
                mx, my = event.pos
                self.update_stick(mx, my)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.active = False
                self.x = self.base_x
                self.y = self.base_y
                self.dx, self.dy = 0.0, 0.0

    def update_stick(self, mx, my):
        dist = math.hypot(mx - self.base_x, my - self.base_y)
        angle = math.atan2(my - self.base_y, mx - self.base_x)
        if dist > self.radius:
            self.x = self.base_x + math.cos(angle) * self.radius
            self.y = self.base_y + math.sin(angle) * self.radius
            self.dx = math.cos(angle)
            self.dy = math.sin(angle)
        else:
            self.x = mx
            self.y = my
            if self.radius > 0:
                self.dx = (mx - self.base_x) / self.radius
                self.dy = (my - self.base_y) / self.radius

    def draw(self, surface):
        self.pulse += 0.2 if self.active else 0.05
        self.ring_rot += 3 if self.active else 0.5
        
        # Draw translucent base
        base_surf = pygame.Surface((self.radius*2 + 40, self.radius*2 + 40), pygame.SRCALPHA)
        center = (self.radius + 20, self.radius + 20)
        
        # Deep military base
        pygame.draw.circle(base_surf, (5, 8, 12, 180), center, self.radius)
        
        # Tech rings
        pygame.draw.circle(base_surf, self.border_color, center, self.radius, width=2)
        pygame.draw.circle(base_surf, (80, 150, 200, 80), center, int(self.radius * 0.7), width=1)
        
        # Rotating radar dashes
        for i in range(4):
            ang = math.radians(self.ring_rot + i * 90)
            ex = center[0] + math.cos(ang) * (self.radius + 5)
            ey = center[1] + math.sin(ang) * (self.radius + 5)
            pygame.draw.circle(base_surf, (150, 220, 255, 255), (int(ex), int(ey)), 4)
            
            # Inner rotating crosshair
            ix = center[0] + math.cos(ang) * (self.radius * 0.4)
            iy = center[1] + math.sin(ang) * (self.radius * 0.4)
            pygame.draw.circle(base_surf, (150, 220, 255, 100), (int(ix), int(iy)), 2)

        surface.blit(base_surf, (self.base_x - center[0], self.base_y - center[1]))
        
        # Dynamic connection line
        if self.active:
            glow_line = math.sin(self.pulse) * 100 + 155
            pygame.draw.line(surface, (100, 200, 255, int(glow_line)), (self.base_x, self.base_y), (self.x, self.y), 4)
            # Arrow head indicating direction
            angle = math.atan2(self.dy, self.dx)
            ax = self.x + math.cos(angle) * 15
            ay = self.y + math.sin(angle) * 15
            pygame.draw.polygon(surface, (150, 220, 255, 200), [
                (ax, ay),
                (self.x + math.cos(angle + 2.5)*15, self.y + math.sin(angle + 2.5)*15),
                (self.x + math.cos(angle - 2.5)*15, self.y + math.sin(angle - 2.5)*15)
            ])
            
        # Draw joystick stick
        stick_surf = pygame.Surface((self.stick_radius*2 + 20, self.stick_radius*2 + 20), pygame.SRCALPHA)
        s_center = (self.stick_radius + 10, self.stick_radius + 10)
        
        # Pulse effect when active
        glow_r = self.stick_radius + int(math.sin(self.pulse)*8) if self.active else self.stick_radius
        pygame.draw.circle(stick_surf, (100, 200, 255, 80 if self.active else 0), s_center, glow_r)
        
        # Core stick
        pygame.draw.circle(stick_surf, (40, 60, 80, 255) if self.active else (30, 45, 60, 255), s_center, self.stick_radius)
        pygame.draw.circle(stick_surf, self.stick_color, s_center, self.stick_radius, 2)
        
        # Inner detail center node
        pygame.draw.circle(stick_surf, (200, 240, 255, 255), s_center, self.stick_radius - 12)
        pygame.draw.circle(stick_surf, (100, 200, 255, 150), s_center, self.stick_radius - 6, 1)
        
        surface.blit(stick_surf, (self.x - s_center[0], self.y - s_center[1]))
