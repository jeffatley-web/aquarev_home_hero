"""Builds the client-logo set for the home page logo marquee.

    python make_logos.py "<Assets/Client Logos dir>" <out dir>        (needs Pillow + numpy)

Every mark comes out as a white-on-transparent file, so the strip needs no CSS filter:
  - vector sources are copied as SVG with every fill / stroke colour rewritten to white,
  - raster sources (boxed logos, PDFs) are knocked out to white PNG at 2x the tallest display size.
Prints one line per logo: file, intrinsic width x height (for the <img> width/height attributes).
"""
import re, sys, shutil, subprocess, tempfile
from pathlib import Path
import numpy as np
from PIL import Image

A, O = Path(sys.argv[1]), Path(sys.argv[2])
O.mkdir(parents=True, exist_ok=True)
H2X = 120          # 2x of the 60 px max display height


def trim(im, pad=0):
    box = im.getchannel('A').point(lambda a: 255 if a > 10 else 0).getbbox()
    im = im.crop(box)
    if pad:
        c = Image.new('RGBA', (im.width + 2 * pad, im.height + 2 * pad), (0, 0, 0, 0)); c.paste(im, (pad, pad)); im = c
    return im


def white(alpha):
    """alpha: float array 0..1 -> white RGBA image"""
    a = (np.clip(alpha, 0, 1) * 255).astype(np.uint8)
    rgba = np.dstack([np.full_like(a, 255)] * 3 + [a])
    return Image.fromarray(rgba, 'RGBA')


def save_png(im, name):
    im = trim(im)
    if im.height > H2X:
        im = im.resize((round(im.width * H2X / im.height), H2X), Image.LANCZOS)
    im.save(O / name, optimize=True)
    print(f'{name:24s} {im.width}x{im.height}')


def ramp(x, lo, hi):
    return np.clip((x - lo) / (hi - lo), 0, 1)


def load(rel):
    return np.asarray(Image.open(A / rel).convert('RGBA')).astype(np.float32)


def colour_distance(px, rgb):
    return np.sqrt(((px[..., :3] - np.array(rgb, np.float32)) ** 2).sum(-1))


# ---- raster knock-outs -------------------------------------------------------------------------
# Days Inn: white wordmark + yellow sun on a blue field -> keep everything brighter than the field
p = load('Days Inn by Wyndham/Days Inn by Wyndham_idsD8BoyHF_1.png')
lum = p[..., :3] @ np.array([.299, .587, .114], np.float32)
save_png(white(ramp(lum, 95, 170) * p[..., 3] / 255), 'days-inn.png')

# Howard Johnson: white wordmark + orange chevron on a teal field -> keep whatever is not the teal
p = load('howard-johnson-hotel-vector-logo-seeklogo/howard-johnson-hotel-seeklogo.png')
field = np.median(p[5:40, 5:40, :3].reshape(-1, 3), axis=0)
save_png(white(ramp(colour_distance(p, field), 40, 110) * p[..., 3] / 255), 'howard-johnson.png')

# Super 8: black script + red 8 on a yellow plate inside a black frame -> keep what is not yellow,
# inside the frame only
p = load('Super 8 by Wyndham/Super 8 by Wyndham_idFjGDdbS6_1.png')
h, w = p.shape[:2]
yellow = np.median(p[h // 2 - 5:h // 2 + 5, 20:40, :3].reshape(-1, 3), axis=0)
a = ramp(colour_distance(p, yellow), 70, 150) * p[..., 3] / 255
inset = int(round(min(h, w) * .045))
a[:inset], a[-inset:], a[:, :inset], a[:, -inset:] = 0, 0, 0, 0
save_png(white(a), 'super-8.png')

# Best Western: vector .ai (PDF) -> raster, drop the tagline line below the lock-up
with tempfile.TemporaryDirectory() as td:
    pdf = Path(td) / 'bw.pdf'; png = Path(td) / 'bw.png'
    shutil.copy(A / 'logo_best_western_hotels_and_resorts.ai', pdf)
    subprocess.run(['sips', '-s', 'format', 'png', '-Z', '1600', str(pdf), '--out', str(png)], check=True, capture_output=True)
    p = np.asarray(Image.open(png).convert('RGBA')).astype(np.float32)
lum = p[..., :3] @ np.array([.299, .587, .114], np.float32)
ink = (1 - ramp(lum, 120, 235)) * p[..., 3] / 255
rows = ink.sum(1) > 1
gaps = [y for y in range(int(len(rows) * .55), len(rows)) if not rows[y]]   # first blank band below the lock-up
if gaps:
    ink[gaps[0]:] = 0
save_png(white(ink), 'best-western.png')

# Marriott: large colour PNG -> silhouette
p = load('marriott-vector-logo-seeklogo/marriott-seeklogo.png')
lum = p[..., :3] @ np.array([.299, .587, .114], np.float32)
save_png(white((1 - ramp(lum, 200, 250)) * p[..., 3] / 255), 'marriott.png')

# ---- vector marks: copy, force every colour to white -------------------------------------------
COLOUR = re.compile(r'(fill|stroke|stop-color)(\s*[:=]\s*["\']?)(#[0-9a-fA-F]{3,8}|rgba?\([^)]*\)|[a-zA-Z]+)')
def svg_white(rel, name, viewbox=None):
    s = (A / rel).read_text(encoding='utf-8')
    # currentColor resolves to black inside <img>, so it is rewritten too
    s = COLOUR.sub(lambda m: m.group(0) if m.group(3).lower() in ('none', 'transparent', 'url') else f'{m.group(1)}{m.group(2)}#fff', s)
    # elements with no fill attribute default to black: make the document default white
    tag = re.search(r'<svg\b[^>]*>', s).group(0)
    if not re.search(r'\sfill=', tag):
        s = s.replace(tag, tag.replace('<svg', '<svg fill="#fff"', 1), 1)
    if viewbox:
        s = re.sub(r'viewBox="[^"]*"', f'viewBox="{viewbox}"', s, count=1)
    (O / name).write_text(s, encoding='utf-8')
    vb = re.search(r'viewBox="([\d.\s-]+)"', s).group(1).split()
    print(f'{name:24s} {float(vb[2]):g}x{float(vb[3]):g}  (viewBox)')

svg_white('The Ritz-Carlton/The Ritz-Carlton_idtK-9NNLE_0.svg', 'ritz-carlton.svg')
svg_white('Hilton Hotels/Hilton Hotels_idIqnH8Vwe_2.svg', 'hilton.svg')
# IHG's artboard carries 117 px clear-space guides in two corners: crop the viewBox to the area between them
svg_white('InterContinental Hotels Group/InterContinental Hotels Group_ihghr-primary-logo-neg-rgb-vert-en_0.svg', 'ihg.svg',
          viewbox='117.168 117.168 694.891 248.867')
svg_white('YMCA/YMCA_Logo_0.svg', 'ymca.svg')
svg_white('Wyndham Hotels & Resorts/Wyndham Hotels & Resorts_idvDSLrNXo_1.svg', 'wyndham.svg')
svg_white('Holiday Inn/Holiday Inn_idXspKs9oZ_0.svg', 'holiday-inn.svg')
svg_white('THE KAHALA/THE KAHALA_idG5sAt3a3_1.svg', 'the-kahala.svg')
svg_white('The Ritz-Carlton O‘ahu/The Ritz-Carlton O‘ahu_idS6WaDJyU_1.svg', 'ocean-bungalows.svg')
