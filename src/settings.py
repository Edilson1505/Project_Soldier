import os

# Pantalla
SCREEN_W, SCREEN_H = 1600, 900
FPS = 60

# Configuración del Sprite
SPRITE_SIZE = 128
SCALE = 2.5
DISPLAY_SIZE = int(SPRITE_SIZE * SCALE)
SPEED = 6

# Balas y Combate
BULLET_SPEED = 25
BULLET_SIZE = 5
MAX_AMMO = 30
MAX_GRENADES = 3

# Configuración de Habitaciones
ROOM_W, ROOM_H = 1200, 960 
PADDING = 800 

ROOMS_MAP = [ (0, 0), (1, 0), (2, 0), (1, 1), (1, -1), (2, 1) ]

min_rx = min(r[0] for r in ROOMS_MAP)
max_rx = max(r[0] for r in ROOMS_MAP)
min_ry = min(r[1] for r in ROOMS_MAP)
max_ry = max(r[1] for r in ROOMS_MAP)

WORLD_W = (max_rx + 1) * ROOM_W + (PADDING * 2)
WORLD_H = (max_ry + 1) * ROOM_H + (PADDING * 2)

# Rutas
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOLDIER_FOLDER = "Soldier_1"

# Frames de Animación y Velocidad (Añadidas Hurt y Dead)
ANIM_FRAMES = {"Idle":7, "Walk":7, "Run":8, "Shot_2":4, "Recharge":13, "Grenade":9, "Explosion":9, "Hurt":3, "Dead":4}
ANIM_SPEED  = {"Idle":10, "Walk":8, "Run":6, "Shot_2":4, "Recharge":5, "Grenade":8, "Explosion":5, "Hurt":5, "Dead":10}
