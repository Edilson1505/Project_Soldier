import os

p = '/home/edilson123/projectsoldier/main.py'

def apply_fix():
    if not os.path.exists(p):
        print("Main file not found")
        return
        
    with open(p, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Change RESIZABLE to SCALED
    if 'pygame.RESIZABLE' in content:
        print("Changing RESIZABLE to SCALED")
        content = content.replace('pygame.RESIZABLE', 'pygame.SCALED')
        
    # 2. Add Crash Catcher
    entry_point = """if __name__ == "__main__":
    main()"""
    
    new_entry_point = """if __name__ == "__main__":
    import traceback
    try:
        main()
    except Exception:
        err = traceback.format_exc()
        print(err)
        
        pygame.init()
        # Fallback screen for errors
        try:
            from src.core.settings import SCREEN_W, SCREEN_H
        except:
            SCREEN_W, SCREEN_H = 400, 600
            
        screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.SCALED)
        pygame.display.set_caption("Error Log")
        font = pygame.font.SysFont(None, 24)
        
        while True:
            screen.fill((120, 0, 0))
            y = 10
            for line in err.splitlines():
                if y > SCREEN_H - 20: break
                txt = font.render(line[:80], True, (255, 255, 255))
                screen.blit(txt, (10, y))
                y += 25
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    import sys; sys.exit()
            
            pygame.display.flip()
            pygame.time.Clock().tick(10)"""
            
    if entry_point in content:
        print("Adding Crash Catcher wrapper")
        content = content.replace(entry_point, new_entry_point)
    else:
        print("Entry point not found, might be slightly different")
        # Try a more flexible replacement
        import re
        content = re.sub(r'if __name__ == "__main__":\s+main\(\)', new_entry_point, content)

    with open(p, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    apply_fix()
