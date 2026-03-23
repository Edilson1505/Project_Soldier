import random
from src.core.settings import SCREEN_W, SCREEN_H, WORLD_W, WORLD_H

class Camera:
    def __init__(self):
        self.x, self.y = 0.0, 0.0 ; self.shake_amt = 0.0
    def update(self, target_x, target_y):
        tx = -target_x + (SCREEN_W // 2) - 32 ; ty = -target_y + (SCREEN_H // 2) - 32
        self.x += (tx - self.x) * 0.1 ; self.y += (ty - self.y) * 0.1
        self.x = max(-(WORLD_W - SCREEN_W), min(0, self.x))
        self.y = max(-(WORLD_H - SCREEN_H), min(0, self.y))
        if self.shake_amt > 0.1: self.shake_amt *= 0.9
        else: self.shake_amt = 0.0
    def add_shake(self, amt): self.shake_amt += amt
    def apply(self, x, y):
        ox = random.uniform(-self.shake_amt, self.shake_amt)
        oy = random.uniform(-self.shake_amt, self.shake_amt)
        return int(x + self.x + ox), int(y + self.y + oy)
