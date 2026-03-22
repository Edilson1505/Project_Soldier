import pygame
import random
from .settings import (SCREEN_W, SCREEN_H, WORLD_W, WORLD_H, DISPLAY_SIZE)

class Camera:
    """Cámara con lerp suave y sistema de sacudida sincronizada (Global Shake)."""
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.lerp = 0.12
        self.shake_amount = 0.0
        # Offset único por frame para que todo vibre junto
        self.offset_x = 0.0
        self.offset_y = 0.0

    def add_shake(self, amount: float):
        self.shake_amount += amount
        if self.shake_amount > 45: self.shake_amount = 45

    def update(self, target_x, target_y):
        # 1. Seguimiento suave
        tx = target_x - SCREEN_W // 2 + DISPLAY_SIZE // 2
        ty = target_y - SCREEN_H // 2 + DISPLAY_SIZE // 2
        self.x += (tx - self.x) * self.lerp
        self.y += (ty - self.y) * self.lerp
        
        # 2. Calcular VIBRACIÓN ÚNICA para este frame
        if self.shake_amount > 0.1:
            self.offset_x = random.uniform(-self.shake_amount, self.shake_amount)
            self.offset_y = random.uniform(-self.shake_amount, self.shake_amount)
            # Decaimiento
            self.shake_amount *= 0.88
        else:
            self.shake_amount = 0
            self.offset_x = 0
            self.offset_y = 0

    def apply(self, x, y):
        """Devuelve posición de pantalla con el desplazamiento global de cámara."""
        return (x - self.x + self.offset_x), (y - self.y + self.offset_y)

    def apply_rect(self, rect: pygame.Rect) -> pygame.Rect:
        """Devuelve un rect sincronizado con la vibración actual."""
        sx, sy = self.apply(rect.x, rect.y)
        return pygame.Rect(sx, sy, rect.width, rect.height)
