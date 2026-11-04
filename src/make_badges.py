"""Trims the brand-approved badge PNGs from Marketing/Website/Assets into img/ at 2x display size.
    python make_badges.py <Assets dir> <out dir>"""
import sys
from pathlib import Path
from PIL import Image, ImageFilter
A, O = Path(sys.argv[1]), Path(sys.argv[2])
O.mkdir(parents=True, exist_ok=True)
H2X = 112   # 2x of the 56 px max display height
def trim(im):
    return im.crop(im.getchannel('A').point(lambda a: 255 if a > 8 else 0).getbbox())
def save(im, name):
    im = trim(im)
    if im.height > H2X:
        im = im.resize((round(im.width * H2X / im.height), H2X), Image.LANCZOS)
    im.save(O / name, optimize=True)
    print(f'{name:18s} {im.width}x{im.height}  {(O / name).stat().st_size / 1024:.1f} KB')
save(Image.open(A / 'Client Logos/iapmo-logo.png').convert('RGBA'), 'iapmo.png')
# White IAPMO for the hero badge row (Jeff, 2026-11-04): oval + shield -> white; the black "IAPMO" letters are
# knocked out where they sit on the shield (navy shows through) and drawn white where they overhang it.
from PIL import ImageDraw
_ia = Image.open(A / 'Client Logos/iapmo-logo.png').convert('RGBA')
_px = _ia.load(); _w, _h = _ia.size
_lum = lambda r, g, b: .299 * r + .587 * g + .114 * b
_shield = [(x, y) for y in range(_h) for x in range(_w) if _px[x, y][3] > 200 and _lum(*_px[x, y][:3]) > 170]
def _hull(pts):                                    # monotone-chain convex hull of the shield's light pixels
    pts = sorted(set(pts))
    def half(seq):
        h = []
        for p in seq:
            while len(h) >= 2 and (h[-1][0]-h[-2][0])*(p[1]-h[-2][1]) - (h[-1][1]-h[-2][1])*(p[0]-h[-2][0]) <= 0:
                h.pop()
            h.append(p)
        return h
    lo, up = half(pts), half(reversed(pts))
    return lo[:-1] + up[:-1]
_m = Image.new('L', _ia.size, 0); ImageDraw.Draw(_m).polygon(_hull(_shield), fill=255)
_m = _m.filter(ImageFilter.MaxFilter(3)); _pm = _m.load()
_out = Image.new('RGBA', _ia.size, (0, 0, 0, 0)); _po = _out.load()
for _y in range(_h):
    for _x in range(_w):
        r, g, b, a = _px[_x, _y]
        ink = min(1.0, max(0.0, (85 - _lum(r, g, b)) / 45))   # 1 = black lettering, 0 = green / light fill
        on_shield = _pm[_x, _y] / 255
        _po[_x, _y] = (255, 255, 255, int(a * (1 - ink * on_shield)))
save(_out, 'iapmo-white.png')
# keep the NSF roundel only (x 22-156, y 8-141 of the 180 px artwork); the caption box below it,
# "Component Certified to NSF/ANSI/CAN 50", is set as live text under the badge row instead
from PIL import ImageDraw
sq = Image.open(A / 'Client Logos/NSF.png').convert('RGBA').crop((22, 8, 156, 141))
w, h = sq.size
m = Image.new('L', (w * 4, h * 4), 0); ImageDraw.Draw(m).ellipse((2, 2, w * 4 - 3, h * 4 - 3), fill=255)
m = m.resize((w, h), Image.LANCZOS)
sq.putalpha(Image.composite(sq.getchannel('A'), Image.new('L', (w, h), 0), m))
save(sq, 'nsf.png')
save(Image.open(A / 'Client Logos/WQA-Logo-Sand-cropped-300x106.png').convert('RGBA'), 'wqa.png')
save(Image.open(A / 'Client Logos/bbb/bbb.png').convert('RGBA'), 'bbb.png')
save(Image.open(A / 'Client Logos/usa.png').convert('RGBA'), 'usa.png')
