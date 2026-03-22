import pygame
import os
from .settings import BASE_DIR, SOLDIER_FOLDER, SPRITE_SIZE, DISPLAY_SIZE

def load_spritesheet(name: str, frame_count: int) -> list:
    """Carga una spritesheet y devuelve una lista de superficies escaladas."""
    path = os.path.join(BASE_DIR, SOLDIER_FOLDER, f"{name}.png")
    sheet = pygame.image.load(path).convert_alpha()
    frames = []
    for i in range(frame_count):
        rect = pygame.Rect(i * SPRITE_SIZE, 0, SPRITE_SIZE, SPRITE_SIZE)
        frame = pygame.transform.scale(sheet.subsurface(rect), (DISPLAY_SIZE, DISPLAY_SIZE))
        frames.append(frame)
    return frames
