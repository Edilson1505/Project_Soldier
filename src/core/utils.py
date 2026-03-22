import pygame
import os
from .settings import SCALE
from .paths import get_asset_path


def load_spritesheet(name: str, count: int) -> list:
    """
    JITTER FIX — UNIFIED CROP ALGORITHM (V2)
    ──────────────────────────────────────
    This version is more robust. It ensures that the frames are divided
    correctly and that the Union-Rect calculation is perfectly aligned
    across the entire animation sequence.

    1. Load sheet.
    2. Divide into 'count' raw frames.
    3. Calculate ONE global Union Bounding Box across all frames.
    4. Crop every frame using that SAME rect.
    5. Scale and return.
    """
    search_paths = [
        get_asset_path(f"Soldier_1/{name}.png"),
        get_asset_path(f"Soldier_2/{name}.png"),
        get_asset_path(f"Soldier_3/{name}.png"),
    ]
    for path in search_paths:
        if not os.path.exists(path):
            continue
        try:
            sheet = pygame.image.load(path).convert_alpha()
            sw, sh = sheet.get_size()
            fw = sw // count   # frame width should now be 128px consistently
            fh = sh

            raw_frames = []
            for i in range(count):
                # Ensure we don't go out of bounds if count calculation is off
                rx = i * fw
                if rx + fw > sw: break
                raw_frames.append(sheet.subsurface((rx, 0, fw, fh)))
            
            if not raw_frames: continue

            # Pass 1: Find Global Bounding Box
            bboxes = [f.get_bounding_rect() for f in raw_frames]
            valid_b = [b for b in bboxes if b.width > 0 and b.height > 0]
            if not valid_b: continue

            u_x1 = min(b.x for b in valid_b)
            u_y1 = min(b.y for b in valid_b)
            u_x2 = max(b.x + b.width  for b in valid_b)
            u_y2 = max(b.y + b.height for b in valid_b)
            
            # Create a shared crop rect based on the union
            # Important: All frames will have the same relative crop
            crop_rect = pygame.Rect(u_x1, u_y1, u_x2 - u_x1, u_y2 - u_y1)

            final_frames = []
            for raw in raw_frames:
                # We crop only the union area
                cropped = raw.subsurface(crop_rect)
                # Scale by the global game scale
                scaled = pygame.transform.scale(
                    cropped, (int(crop_rect.width * SCALE), int(crop_rect.height * SCALE))
                )
                final_frames.append(scaled)

            return final_frames

        except Exception as e:
            print(f"Error loading {name}: {e}")

    return []
