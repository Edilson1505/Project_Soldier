import pygame
from .settings import (ROOM_W, ROOM_H, ROOMS_MAP, PADDING, SCALE)

class RoomWorld:
    """Mundo Side-2D con Vacío exterior y suelo limitado a las habitaciones."""
    def __init__(self):
        self.walls = []
        self._generate_metal_bunker()
        self.tile_size = 160 # Tamaño de baldosa de hormigón

    def _generate_metal_bunker(self):
        self.walls = []
        for rx, ry in ROOMS_MAP:
            x, y = rx * ROOM_W + PADDING, ry * ROOM_H + PADDING
            
            # Generar muros de 80x80 por el perímetro
            for i in range(0, ROOM_W, 80):
                if self._should_add_wall(rx, ry-1): # Techo
                    self.walls.append(pygame.Rect(x + i, y, 80, 80))
                if self._should_add_wall(rx, ry+1): # Suelo
                    self.walls.append(pygame.Rect(x + i, y + ROOM_H - 80, 80, 80))
            
            for j in range(0, ROOM_H, 80):
                if self._should_add_wall(rx-1, ry): # Izquierda
                    self.walls.append(pygame.Rect(x, y + j, 80, 80))
                if self._should_add_wall(rx+1, ry): # Derecha
                    self.walls.append(pygame.Rect(x + ROOM_W - 80, y + j, 80, 80))

    def _should_add_wall(self, nx, ny):
        return (nx, ny) not in ROOMS_MAP

    def draw(self, surface, camera):
        sw, sh = surface.get_size()
        
        # 🌌 DIBUJAR SÓLO SUELO DENTRO DE LAS HABITACIONES
        for rx, ry in ROOMS_MAP:
            # Límites de la habitación actual
            room_x, room_y = rx * ROOM_W + PADDING, ry * ROOM_H + PADDING
            
            # Dibujar mosaico de hormigón solo en este rectángulo
            for tx in range(room_x, room_x + ROOM_W, self.tile_size):
                for ty in range(room_y, room_y + ROOM_H, self.tile_size):
                    draw_pos = camera.apply(tx, ty)
                    # Solo dibujar si está cerca de la pantalla
                    if -self.tile_size < draw_pos[0] < sw and -self.tile_size < draw_pos[1] < sh:
                        pygame.draw.rect(surface, (25, 25, 32), (draw_pos[0], draw_pos[1], self.tile_size-2, self.tile_size-2))
                        # Detalle de rejilla metálica sutil
                        pygame.draw.rect(surface, (35, 35, 45), (draw_pos[0], draw_pos[1], self.tile_size, self.tile_size), 1)

        # 🧱 DIBUJAR MUROS (Side-2D Plano)
        for rect in self.walls:
            draw_rect = camera.apply_rect(rect)
            if draw_rect.colliderect(surface.get_rect()):
                pygame.draw.rect(surface, (45, 45, 55), draw_rect) # Fondo bloque
                pygame.draw.line(surface, (80, 80, 100), draw_rect.topleft, draw_rect.topright, 2) # Brillo
                pygame.draw.line(surface, (80, 80, 100), draw_rect.topleft, draw_rect.bottomleft, 2)
                pygame.draw.line(surface, (20, 20, 25), draw_rect.bottomleft, draw_rect.bottomright, 2) # Sombra
                pygame.draw.line(surface, (20, 20, 25), draw_rect.topright, draw_rect.bottomright, 2)
                
                # Remaches Decorativos
                for r_pos in [(10,10), (10, 60), (60, 10), (60, 60)]:
                    pygame.draw.circle(surface, (20, 20, 25), (draw_rect.x + r_pos[0], draw_rect.y + r_pos[1]), 3)
