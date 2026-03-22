import random

# ── Display ───────────────────────────────────────────────────────────────────
SCREEN_W, SCREEN_H = 1280, 800
FPS         = 60

# ── Physics ───────────────────────────────────────────────────────────────────
SPEED       = 5
SCALE       = 2
DISPLAY_SIZE = 64 * SCALE

# ── World ─────────────────────────────────────────────────────────────────────
ROOM_W      = 960
ROOM_H      = 720
PADDING     = 200
WORLD_W     = PADDING * 2 + ROOM_W * 5 + 400
WORLD_H     = PADDING * 2 + ROOM_H
DOOR_W      = 180
WALL_T      = 56

ROOMS_MAP   = [(0,0), (1,0), (2,0), (3,0), (4,0)]
SAFE_ROOM   = 0

# ── Ammo ─────────────────────────────────────────────────────────────────────
MAX_AMMO    = 30
MAX_GRENADES = 5

# ── Animation (Updated with corrected counts) ──────────────────────────────────
# Based on 128px-wide frame analysis:
ANIM_FRAMES = {
    "Idle":     7,   # 896 / 128 = 7
    "Walk":     7,   # 896 / 128 = 7
    "Run":      8,   # 1024 / 128 = 8
    "Shot_1":   4,   # 512 / 128 = 4
    "Shot_2":   4,   # 512 / 128 = 4
    "Recharge": 13,  # 1664 / 128 = 13
    "Grenade":  9,   # 1152 / 128 = 9
    "Explosion": 9,  # 1152 / 128 = 9
    "Hurt":     3,   # 384 / 128 = 3 (approx)
    "Dead":     4,   # 512 / 128 = 4
}

ANIM_SPEED  = {
    "Idle":    12,   # Made slower for breathing effect
    "Walk":     8,
    "Run":      6,
    "Shot_2":   4,
    "Recharge": 4,
    "Grenade":  5,
    "Explosion":3,
    "Hurt":     4,
}

# ── Colors ────────────────────────────────────────────────────────────────────
WALL_COLOR  = (28, 33, 46)
GROUND_COLOR = (14, 17, 22)
WALL_HL     = (55, 80, 125)
