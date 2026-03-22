import os
import re

p = '/home/edilson123/projectsoldier/main.py'

def apply_final_fix():
    if not os.path.exists(p):
        print("Main file not found")
        return
        
    with open(p, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Look for global Pygame calls (not in functions/classes)
    # We'll just find the lines after imports but before first 'def' or 'class'
    lines = content.splitlines()
    new_lines = []
    global_code = []
    
    in_global_zone = False
    
    for line in lines:
        sline = line.strip()
        if not sline or sline.startswith('#') or sline.startswith('import') or sline.startswith('from'):
            new_lines.append(line)
            continue
        
        if sline.startswith('def ') or sline.startswith('class '):
            in_global_zone = False
            new_lines.append(line)
            continue
            
        # If we hit any other code before first def/class, it's global init
        if not in_global_zone and not sline.startswith('def ') and not sline.startswith('class '):
            # Find the index of the first function
            first_def = content.find('\ndef ')
            if first_def == -1: first_def = content.find('def ')
            
            # This is complex, let's just use string replacement for known bad lines
            content = content.replace('pygame.font.init()', '# moved: pygame.font.init()')
            content = content.replace('pygame.mixer.init(', '# moved: pygame.mixer.init(')
            
            # Find and comment out global Sound loads
            content = re.sub(r'(snd_\w+\s*=\s*pygame\.mixer\.Sound)', r'# moved: \1', content)
            
            # Inject them into main()
            init_code = """
    pygame.init()
    pygame.font.init()
    pygame.mixer.init(44100, -16, 2, 512)
    global snd_shot, snd_reload, snd_step, snd_btn # ensure they are accessible if needed globally
    try:
        snd_shot = pygame.mixer.Sound("shot1.mp3")
        snd_reload = pygame.mixer.Sound("reload1.mp3")
        snd_step = pygame.mixer.Sound("walking1.mp3")
        snd_btn = pygame.mixer.Sound("button_sound.mp3")
    except Exception as e:
        print(f"Error loading initial sounds: {e}")
"""
            content = re.sub(r'def main\(\):', 'def main():' + init_code, content)
            break

    with open(p, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Code moved successfully")

if __name__ == "__main__":
    apply_final_fix()
