#!/usr/bin/env python3
"""Prepare high-resolution OQB presentation art for Luma3DS and Sharkive."""
from pathlib import Path
import math
import urllib.request

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / '.local/asset-sources'
CACHE.mkdir(parents=True, exist_ok=True)
LUMA_URL = 'https://avatars.githubusercontent.com/u/65085206?s=512&v=4'


def gradient(size, stops):
    w, h = size
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    t = np.clip((x / w * .72 + y / h * .28), 0, 1)[..., None]
    c0 = np.array(stops[0], dtype=np.float32)
    c1 = np.array(stops[1], dtype=np.float32)
    return Image.fromarray(np.uint8(np.clip(c0 * (1 - t) + c1 * t, 0, 255)), 'RGB').convert('RGBA')


def save_icon(app, image):
    out = ROOT / 'assets/community' / app
    out.mkdir(parents=True, exist_ok=True)
    image.convert('RGBA').resize((512, 512), Image.Resampling.LANCZOS).save(out / 'icon.webp', quality=95)


def save_background(app, image):
    out = ROOT / 'assets/community' / app
    out.mkdir(parents=True, exist_ok=True)
    image.convert('RGB').save(out / 'background.webp', quality=93)


# LumaTeam's official star avatar, supplied by the user, on a harmonious mint/navy tile.
luma_source = CACHE / 'luma-team.png'
if not luma_source.exists():
    with urllib.request.urlopen(LUMA_URL, timeout=30) as response:
        luma_source.write_bytes(response.read())
star = Image.open(luma_source).convert('RGBA')
star.thumbnail((400, 400), Image.Resampling.LANCZOS)
luma = gradient((512, 512), ((16, 37, 50), (32, 75, 80)))
d = ImageDraw.Draw(luma)
for radius, alpha in ((220, 18), (170, 24), (120, 30)):
    d.ellipse((256-radius, 256-radius, 256+radius, 256+radius), outline=(137, 240, 226, alpha), width=3)
luma.alpha_composite(star, ((512-star.width)//2, (512-star.height)//2))
save_icon('luma3ds', luma)

# Sharkive's existing sailboat symbol, rebuilt cleanly at high resolution.
n = 2048
shark = Image.new('RGBA', (n, n))
d = ImageDraw.Draw(shark)
d.rounded_rectangle((0, 0, n-1, n-1), radius=n*.23, fill='#103B64')
d.polygon([(n*.17,n*.68),(n*.42,n*.24),(n*.55,n*.55),(n*.82,n*.68)], fill='#73C8F2')
d.polygon([(n*.17,n*.74),(n*.83,n*.74),(n*.58,n*.86),(n*.31,n*.86)], fill='#D6F3FF')
d.ellipse((n*.62,n*.59,n*.67,n*.64), fill='#103B64')
save_icon('sharkive', shark)

# Original backgrounds: no external artwork and no text near the animated crop edges.
luma_bg = gradient((1200, 675), ((10, 25, 38), (30, 78, 81)))
d = ImageDraw.Draw(luma_bg, 'RGBA')
for x, y, r in ((1030,110,190),(1030,110,130),(160,555,150)):
    d.ellipse((x-r,y-r,x+r,y+r), outline=(127,234,218,32), width=3)
for i in range(38):
    x = (i * 197 + 83) % 1160 + 20
    y = (i * 109 + 47) % 615 + 30
    r = 2 + (i % 3)
    d.ellipse((x-r,y-r,x+r,y+r), fill=(172,245,231,45+(i%4)*15))
save_background('luma3ds', luma_bg)

shark_bg = gradient((1200, 675), ((5, 24, 48), (23, 117, 174)))
d = ImageDraw.Draw(shark_bg, 'RGBA')
for row in range(7):
    y0 = 105 + row * 82
    points = []
    for x in range(-40, 1241, 12):
        y = y0 + math.sin(x / 105 + row * .7) * 18
        points.append((x, y))
    d.line(points, fill=(128,220,250,24+row*3), width=3)
for i in range(24):
    x = (i * 173 + 61) % 1140 + 30
    y = (i * 137 + 89) % 585 + 35
    r = 3 + (i % 4) * 2
    d.ellipse((x-r,y-r,x+r,y+r), outline=(194,239,255,45), width=2)
save_background('sharkive', shark_bg)
print('Prepared 512px icons and 1200x675 backgrounds for Luma3DS and Sharkive.')
