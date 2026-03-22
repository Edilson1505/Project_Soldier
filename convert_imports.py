import os
import re

p = '/home/edilson123/projectsoldier/src'

def convert_to_absolute():
    for root, dirs, files in os.walk(p):
        for filename in files:
            if filename.endswith('.py'):
                filepath = os.path.join(root, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Determine how many levels up 'src' is from this file
                # src/ is at level 0
                # src/core/ is at level 1
                # src/ui/screens/ is at level 2
                rel_path = os.path.relpath(root, p)
                level = 0 if rel_path == '.' else len(rel_path.split(os.sep))
                
                # from .settings -> from src.core.settings (if in core)
                # but it's simpler to just target the 'src' package directly
                
                # from ...core -> from src.core
                # from ..core -> from src.core
                # from .settings -> from src.ui.screens.settings (no, that's not right)
                
                # Actually, the user's project structure is:
                # src/core
                # src/ui/screens
                # src/entities
                
                # Let's use a more robust regex to replace relative dots
                # based on the current file's position relative to 'src'
                
                def replace_dots(match):
                    dots = match.group(1)
                    module = match.group(2)
                    num_dots = len(dots)
                    
                    # Convert to absolute based on current root
                    parts = root.split(os.sep)
                    src_idx = parts.index('src')
                    
                    # Target package is parts[src_idx] which is 'src'
                    # plus any remaining parts minus the num_dots
                    target_parts = parts[src_idx : len(parts) - (num_dots - 1)]
                    return f"from {'.'.join(target_parts)}.{module}"

                # from ...core.settings -> from src.core.settings
                # Regex for: 'from ' + (one or more dots) + (module name) + ' import'
                new_content = re.sub(r'from (\.+)([\w\.]+) import', replace_dots, content)
                
                if content != new_content:
                    print(f"Update imports in: {filepath}")
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)

if __name__ == "__main__":
    convert_to_absolute()
