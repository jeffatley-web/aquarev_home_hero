"""Trims the brand-approved badge PNGs from Marketing/Website/Assets into img/ at 2x display size.
    python make_badges.py <Assets dir> <out dir>"""
import sys
from pathlib import Path
from PIL import Image
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
