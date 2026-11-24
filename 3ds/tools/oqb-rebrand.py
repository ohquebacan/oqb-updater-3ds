#!/usr/bin/env python3
"""Regenerate only the OQB brand art and UI palette; never rebuild catalog/game art."""
import importlib.util, json, math, struct, zlib
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[2]
GEN = ROOT / '3ds/build/gen'
GFX = ROOT / '3ds/romfs/gfx'
GEN.mkdir(parents=True, exist_ok=True)
spec = importlib.util.spec_from_file_location('pack', ROOT / '3ds/tools/pack.py')
pack = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pack)
LOGO = Image.open(ROOT / 'assets/brand/oqb-icon.png').convert('RGBA')
FONT = '/System/Library/Fonts/Supplemental/Arial Bold.ttf'
REGULAR = '/System/Library/Fonts/Supplemental/Arial.ttf'

def rounded_logo(size):
    im = LOGO.resize((size, size), Image.Resampling.LANCZOS)
    mask = Image.new('L', (size, size))
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size - 1, size - 1), radius=round(size * .22), fill=255)
    im.putalpha(mask)
    # Remove the isolated cyan source pixel exposed by low-resolution resampling.
    px = np.array(im)
    stray = (px[:, :, 0] < 80) & (px[:, :, 1] > 180) & (px[:, :, 2] > 180) & (px[:, :, 3] > 0)
    px[stray] = (0, 0, 0, 255)
    return Image.fromarray(px, 'RGBA')

def text_image(text, width, height, font_size, bold=True):
    im = Image.new('RGBA', (width * 4, height * 4))
    font = ImageFont.truetype(FONT if bold else REGULAR, font_size * 4)
    d = ImageDraw.Draw(im)
    box = d.textbbox((0, 0), text, font=font)
    d.text(((im.width - (box[2] - box[0])) / 2 - box[0], (im.height - (box[3] - box[1])) / 2 - box[1]), text, font=font, fill='white')
    return im.resize((width, height), Image.Resampling.LANCZOS)

for name, args in [('title', ('OQB UPDATER', 264, 34, 26)), ('welcome', ('TODO EN UNO', 180, 14, 10)),
                   ('wordmark', ('OQB UPDATER', 192, 30, 22)), ('emblem', ('', 0, 0, 0))]:
    if args[0]:
        text_image(*args).save(GEN / f'{name}.png')
for name, size in [('emblem', 76), ('emblem-small', 48)]:
    im = Image.new('RGBA', (size, size))
    im.paste(rounded_logo(size), (0, 0), rounded_logo(size))
    im.save(GEN / f'{name}.png')

# Preserve the existing control badges, halo and shadow; replace brand images only.
def decode_sheet(path):
    b = path.read_bytes()
    magic, w, h, fmt, count, _ = struct.unpack_from('<4sHHBBH', b)
    if magic != b'FTX1' or fmt != 0:
        raise ValueError(f'Unsupported brand atlas: {path}')
    off = 12 + count * 8
    raw_size, zsize = struct.unpack_from('<II', b, off)
    raw = zlib.decompress(b[off + 8:off + 8 + zsize])
    px = np.frombuffer(raw, dtype=np.uint8).reshape(h, w, 4)
    idx = pack.morton_index(w, h)
    canvas = np.zeros((h, w, 4), dtype=np.uint8)
    canvas.reshape(-1, 4)[:] = px.reshape(-1, 4)[idx][:, [3, 2, 1, 0]]
    images = []
    for i in range(count):
        x, y, iw, ih = struct.unpack_from('<HHHH', b, 12 + i * 8)
        images.append(Image.fromarray(canvas[y:y+ih, x:x+iw].copy(), 'RGBA'))
    return images

names = json.loads((GFX / 'ui.json').read_text())
old = decode_sheet(GFX / 'ui.ftx')
images = []
for name, previous in zip(names, old):
    p = GEN / f'{name}.png'
    if name == 'sb-emblem':
        images.append(rounded_logo(previous.width))
    else:
        images.append(Image.open(p).convert('RGBA') if p.exists() else previous)
pack.write_sheet(GFX / 'ui.ftx', images, pack.RGBA8)

def theme_icon(name, size):
    """Purpose-made sun and moon tiles; no miniature store wordmark."""
    n = max(4, size * 4)
    im = Image.new('RGBA', (n, n))
    d = ImageDraw.Draw(im)
    bg = '#F7E8B5' if name == 'light' else '#202640'
    d.rounded_rectangle((0, 0, n-1, n-1), radius=n*.23, fill=bg)
    cx = cy = n*.5
    if name == 'light':
        for i in range(8):
            a = i*math.tau/8
            d.line((cx+math.cos(a)*n*.29,cy+math.sin(a)*n*.29,
                    cx+math.cos(a)*n*.37,cy+math.sin(a)*n*.37), fill='#E7A42C', width=round(n*.047))
        d.ellipse((n*.28,n*.28,n*.72,n*.72), fill='#FFC94F')
        d.ellipse((n*.34,n*.32,n*.57,n*.46), fill=(255,239,162,130))
    else:
        d.ellipse((n*.27,n*.23,n*.73,n*.73), fill='#F5E9BA')
        d.ellipse((n*.41,n*.15,n*.79,n*.62), fill=bg)
        for x,y,r in ((.27,.27,.028),(.72,.31,.035),(.73,.68,.025),(.31,.73,.022)):
            d.ellipse(((x-r)*n,(y-r)*n,(x+r)*n,(y+r)*n), fill='#B9C9FF')
    return im.resize((size,size),Image.Resampling.LANCZOS)

# Same pose metadata and texture sizes as the original animated brand pieces.
meta = json.loads((GFX / 'coins.json').read_text())
for name, m in meta.items():
    w, h = m['w'], m['h']
    frames = []
    for i in range(m['wobble']):
        pose = i / max(1, m['wobble'] - 1)
        size = round(m['size'] * (.90 + .10 * math.sin(math.pi * pose)))
        im = Image.new('RGBA', (w, h))
        logo = theme_icon(name,size) if name in ('light','dark') else rounded_logo(size)
        x, y = round(m['cx'] - size / 2), round(m['cy'] - size / 2)
        if name in ('light', 'dark'):
            d = ImageDraw.Draw(im)
            d.rounded_rectangle((x - 5, y - 5, x + size + 4, y + size + 4), radius=18,
                                fill=(242, 245, 240, 255) if name == 'light' else (18, 23, 17, 255),
                                outline=(86, 168, 74, 180), width=2)
        im.alpha_composite(logo, (x, y))
        frames.append(im)
    pack.write_sheet(GFX / f'coin-{name}.ftx', frames, pack.RGBA8)
    if m['spin']:
        spins = []
        for i in range(m['spin']):
            size = round(m['size'])
            narrow = max(3, round(size * abs(math.cos(2 * math.pi * i / m['spin']))))
            im = Image.new('RGBA', (w, h))
            tile = theme_icon(name,size) if name in ('light','dark') else rounded_logo(size)
            logo = tile.resize((narrow, size), Image.Resampling.LANCZOS)
            im.alpha_composite(logo, (round(m['cx'] - narrow / 2), round(m['cy'] - size / 2)))
            spins.append(im)
        pack.write_sheet(GFX / f'coin-{name}-spin.ftx', spins, pack.RGBA8)

# Subtle OQB dot-grid backgrounds, preserving the native drift margins.
for top in (True, False):
    for dark in (True, False):
        w, h = (414, 254) if top else (334, 254)
        # Neutral white artwork is tinted at runtime with TH.bg for every accent.
        im = Image.new('RGBA', (w, h), '#FFFFFF')
        d = ImageDraw.Draw(im)
        dot = (115, 115, 115, 255)
        for y in range(8, h, 20):
            for x in range(8, w, 20):
                d.ellipse((x, y, x + 1, y + 1), fill=dot)
        name = f'bg-{"top" if top else "bottom"}-{"dark" if dark else "light"}'
        im.convert('RGB').save(GEN / f'{name}.png')
        pack.write_sheet(GFX / f'{name}.ftx', [im], pack.RGB8)

rounded_logo(48).save(ROOT / '3ds/meta/icon.png')

theme_icon('light',96).save(GEN / 'theme-light.png')
theme_icon('dark',96).save(GEN / 'theme-dark.png')
# Grid atlases are owned by render-home-icons.py, including every rounded mask.
print('OQB brand atlas, theme icons, static emblem and HOME icon regenerated.')
