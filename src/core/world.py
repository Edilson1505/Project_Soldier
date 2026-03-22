import pygame
import random
from .settings import (ROOMS_MAP, ROOM_W, ROOM_H, PADDING,
                        WALL_T, DOOR_W, WALL_COLOR, GROUND_COLOR, WALL_HL)

# Bunker Palette
_FLOOR_BRICK_1 = (18, 20, 26)
_FLOOR_BRICK_2 = (22, 25, 32)
_WALL_CONCRETE = (32, 38, 50)
_REBAR_COLOR   = (45, 55, 75)

def _room_rect(col: int, row: int) -> pygame.Rect:
    return pygame.Rect(PADDING + col * ROOM_W, PADDING + row * ROOM_H, ROOM_W, ROOM_H)

class RoomWorld:
    def __init__(self):
        self.rooms  = [_room_rect(c, r) for c, r in ROOMS_MAP]
        self.walls  = []
        self.props  = [] # Eliminated crates as requested
        self._doors = []

        self._build_walls()

    def _build_walls(self):
        adj = set()
        for i, (ca, ra) in enumerate(ROOMS_MAP):
            for cb, rb in ROOMS_MAP[i+1:]:
                if ra == rb and abs(ca - cb) == 1:
                    adj.add((min(ca, cb), max(ca, cb)))

        for idx, (col, row) in enumerate(ROOMS_MAP):
            r = self.rooms[idx]
            door_cy = r.centery
            door_top    = door_cy - DOOR_W // 2
            door_bottom = door_cy + DOOR_W // 2

            has_left_door  = (col - 1, col) in adj
            has_right_door = (col, col + 1) in adj

            # TOP
            self.walls.append(pygame.Rect(r.x, r.y, r.w, WALL_T))
            # BOTTOM
            self.walls.append(pygame.Rect(r.x, r.bottom - WALL_T, r.w, WALL_T))

            # LEFT
            if has_left_door:
                top_h = max(0, door_top - r.y)
                bot_h = max(0, r.bottom - door_bottom)
                if top_h > 0: self.walls.append(pygame.Rect(r.x, r.y, WALL_T, top_h))
                if bot_h > 0: self.walls.append(pygame.Rect(r.x, door_bottom, WALL_T, bot_h))
                self._doors.append(pygame.Rect(r.x, door_top, WALL_T, DOOR_W))
            else:
                self.walls.append(pygame.Rect(r.x, r.y, WALL_T, r.h))

            # RIGHT
            if has_right_door:
                top_h = max(0, door_top - r.y)
                bot_h = max(0, r.bottom - door_bottom)
                if top_h > 0: self.walls.append(pygame.Rect(r.right - WALL_T, r.y, WALL_T, top_h))
                if bot_h > 0: self.walls.append(pygame.Rect(r.right - WALL_T, door_bottom, WALL_T, bot_h))
                self._doors.append(pygame.Rect(r.right - WALL_T, door_top, WALL_T, DOOR_W))
            else:
                self.walls.append(pygame.Rect(r.right - WALL_T, r.y, WALL_T, r.h))

    def _draw_brick_floor(self, surface, cam, room_rect):
        gx, gy = cam.apply(room_rect.x, room_rect.y)
        bw, bh = 120, 60 # Brick size
        
        # Clip drawing to the room area
        for iy in range(0, room_rect.h, bh):
            # Stagger every other row
            offset = (bw // 2) if (iy // bh) % 2 == 1 else 0
            for ix in range(-bw, room_rect.w + bw, bw):
                bx, by = gx + ix + offset, gy + iy
                # Only draw if within room bounds plus a bit of overlap
                rect = pygame.Rect(bx, by, bw, bh)
                col = _FLOOR_BRICK_1 if (ix // bw + iy // bh) % 2 == 0 else _FLOOR_BRICK_2
                pygame.draw.rect(surface, col, rect)
                # Brick border
                pygame.draw.rect(surface, (10, 12, 18), rect, 1)

    def draw(self, surface, cam):
        # 1. Brick Floors
        for r in self.rooms:
            self._draw_brick_floor(surface, cam, r)
            gx, gy = cam.apply(r.x, r.y)
            pygame.draw.rect(surface, WALL_HL, (gx, gy, r.w, r.h), 4)

        # 2. Door gaps
        for d in self._doors:
            dx, dy = cam.apply(d.x, d.y)
            pygame.draw.rect(surface, _FLOOR_BRICK_1, (dx, dy, d.w, d.h))
            pygame.draw.rect(surface, WALL_HL, (dx, dy, d.w, d.h), 2)

        # 3. Bunker Walls (Concrete style)
        for w in self.walls:
            wx, wy = cam.apply(w.x, w.y)
            pygame.draw.rect(surface, _WALL_CONCRETE, (wx, wy, w.w, w.h))
            # Heavy reinforcement lines
            if w.w > w.h:
                for i in range(0, w.w, 80):
                    pygame.draw.line(surface, _REBAR_COLOR, (wx+i, wy), (wx+i, wy+w.h), 2)
            else:
                for i in range(0, w.h, 80):
                    pygame.draw.line(surface, _REBAR_COLOR, (wx, wy+i), (wx+w.w, wy+i), 2)
            pygame.draw.rect(surface, WALL_HL, (wx, wy, w.w, w.h), 2)
