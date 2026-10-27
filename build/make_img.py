"""Responsive WebP copies of the site's photos (assets/img/*.jpg|png -> name-480.webp, name-960.webp, name-1440.webp).
The page asks for the size that fits the screen, so a phone downloads a fraction of the original. Skips files already made.
Run from the repo root: python3 build/make_img.py"""
import glob, os
from PIL import Image
made = 0
for src in glob.glob('assets/img/*.jpg') + glob.glob('assets/img/*.jpeg') + glob.glob('assets/img/*.png'):
    base = os.path.splitext(src)[0]
    im = None
    for w in (480, 960, 1440):
        out = f'{base}-{w}.webp'
        if os.path.exists(out) and os.path.getmtime(out) >= os.path.getmtime(src):
            continue
        im = im or Image.open(src).convert('RGB')
        r = min(1, w / im.width)
        im.resize((max(1, int(im.width * r)), max(1, int(im.height * r))), Image.LANCZOS).save(out, 'WEBP', quality=78, method=6)
        made += 1
print(f'images: {made} webp variants written')
