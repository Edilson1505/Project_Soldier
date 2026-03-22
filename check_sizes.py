import struct, os

def png_size(path):
    with open(path, 'rb') as f:
        f.read(8)
        f.read(4)
        f.read(4)
        w, h = struct.unpack('>II', f.read(8))
        return w, h

base = r'C:\Users\galle\Documents\Project Soldier'
for s in ['Soldier_1', 'Soldier_2', 'Soldier_3']:
    print(f'=== {s} ===')
    folder = os.path.join(base, s)
    for fn in sorted(os.listdir(folder)):
        w, h = png_size(os.path.join(folder, fn))
        frames = w // h
        print(f'  {fn}: {w}x{h}  frames={frames}')
