import os
import sys

# Get the directory where the main script (main.py) is located
if getattr(sys, 'frozen', False):
    # If the app is bundled (e.g., by PyInstaller or similar)
    BASE_DIR = os.path.dirname(sys.executable)
elif 'ANDROID_ARGUMENT' in os.environ or 'ANDROID_PRIVATE_PATH' in os.environ:
    # On Android, the current working directory is the app's internal storage
    BASE_DIR = os.getcwd()
else:
    # If running from source, main.py is in the parent of the 'src' directory
    # Current file is in src/core/paths.py, so we go up two levels
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_asset_path(relative_path):
    """Returns the absolute path to an asset file."""
    # Ensure relative_path uses the correct separator for the OS
    rel_path = relative_path.replace("\\", "/").replace("/", os.sep)
    return os.path.join(BASE_DIR, rel_path)

def get_data_path(filename):
    """Returns a writeable path for data files like highscores."""
    # On Android, we should use the internal private path if available
    base = os.environ.get('ANDROID_PRIVATE_PATH', BASE_DIR)
    
    # Check if the folder is potentially writeable
    # In some Android environments, the base 'app' folder is read-only
    data_dir = os.path.join(base, "data")
    if not os.path.exists(data_dir):
        try:
            os.makedirs(data_dir, exist_ok=True)
        except:
            # If we can't create 'data' folder, use the base dir directly
            # On Android, 'base' (data/data/pkg/files/app) should be writeable
            return os.path.join(base, filename)
    return os.path.join(data_dir, filename)

def get_safe_font(name, size, bold=False, italic=False):
    """
    Attempts to load a specific system font, falling back to 
    the default pygame font if not found.
    """
    import pygame
    # Try the requested font
    font = pygame.font.SysFont(name, size, bold=bold, italic=italic)
    # Check if the returned font is the default one (meaning requested failed)
    # Pygame doesn't always make it easy to tell, but we can check match_font
    if not pygame.font.match_font(name):
        # Fallback to default
        return pygame.font.SysFont(None, size, bold=bold, italic=italic)
    return font
