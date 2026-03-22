import os

# Path in WSL format for the project
p = '/home/edilson123/projectsoldier'

def fix_fonts(directory):
    for root, dirs, files in os.walk(directory):
        # Skip Buildozer and pycache
        if '.buildozer' in root or '__pycache__' in root:
            continue
        for filename in files:
            if filename.endswith('.py'):
                filepath = os.path.join(root, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if 'SysFont("Consolas"' in content:
                        print(f"Fixing fonts in: {filepath}")
                        new_content = content.replace('SysFont("Consolas"', 'SysFont(None')
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")

if __name__ == "__main__":
    if os.path.exists(p):
        fix_fonts(p)
    else:
        print(f"Path not found: {p}")
