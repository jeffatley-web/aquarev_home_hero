"""Renders the home hero background loop from the text-free plate.

    python render_loop.py plate.png ../media

Outputs (all seamless 12 s loops, silent, H.264, frame 0 == poster):
    hero-desktop.mp4 / .jpg / .webp   1600x900 full frame (16:9)
    hero-mobile.mp4  / .jpg / .webp   720x760 crop on the product (phones / narrow tablets)

Every motion term runs on a whole number of cycles per 12 s, so the last frame flows into
the first with no visible jump. Coordinates are in the 1672x941 concept / plate space.
"""
import sys, math, random, subprocess
from pathlib import Path
import cv2, numpy as np
import imageio_ffmpeg
from PIL import Image

PLATE, OUT = Path(sys.argv[1]), Path(sys.argv[2])
FPS, T = 24, 12.0
N = int(FPS * T)
W_ = 2 * math.pi / T          # one cycle per loop
plate = cv2.imread(str(PLATE))
H, W = plate.shape[:2]        # 941 x 1672

def smooth(a):
    a = np.clip(a, 0., 1.)
    return a * a * (3. - 2. * a)

# ---- water ribbon either side of the product: gentle refraction wobble, product body protected
rx0, ry0, rx1, ry1 = 805, 240, W, 660
rh, rw = ry1 - ry0, rx1 - rx0
yr, xr = np.mgrid[0:rh, 0:rw].astype(np.float32)
absx = xr + rx0
rib_a = smooth(xr / 100) * smooth((rw - xr) / 24) * smooth(yr / 110) * smooth((rh - yr) / 95)
rib_a *= 1.0 - 0.98 * smooth((absx - 1092) / 75) * (1 - smooth((absx - 1328) / 90))
rib_a = np.clip(rib_a * 0.7, 0, 0.7)[..., None]

# ---- pool floor: slow caustic drift, the product's base column protected
fy0 = 790
fh = H - fy0
yb, xb = np.mgrid[0:fh, 0:W].astype(np.float32)
floor_a = smooth(yb / 40) * 0.7
base = smooth((xb - 1150) / 30) * (1 - smooth((xb - 1340) / 30)) * (1 - smooth((yb - 40) / 20))
floor_a = (floor_a * (1 - base))[..., None]

# ---- light rays at the surface: soft breathing
ty1 = 260
yt, xt = np.mgrid[0:ty1, 0:W].astype(np.float32)
ray_mask = (np.exp(-((xt - 1240) / 260) ** 2) * (1 - yt / ty1))[..., None]

# ---- bubbles: each lives for T/n seconds and repeats exactly n times per loop
rng = random.Random(71822)
bubbles = []
for _ in range(54):
    n = rng.choice([1, 1, 2, 2, 3])
    bubbles.append(dict(
        x=rng.uniform(830, W - 20), y0=rng.uniform(260, H - 120), rise=rng.uniform(160, 420),
        r=rng.uniform(1.2, 4.2), n=n, ph=rng.random(), sway=rng.uniform(4, 11), sp=rng.uniform(0, 2 * math.pi)))

# ---- halo tracer: one full lap per loop
CX, CY, HRX, HRY = 1247, 408, 306, 291


def frame_at(t):
    f = plate.copy()
    # ribbon wobble
    xm = xr + (3.6 * np.sin(yr / 44. + 2 * W_ * t) + 1.8 * np.sin(xr / 82. - 1 * W_ * t)).astype(np.float32)
    ym = yr + (2.2 * np.sin(xr / 68. + 2 * W_ * t)).astype(np.float32)
    roi = f[ry0:ry1, rx0:rx1]
    warped = cv2.remap(roi, xm, ym, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    roi[:] = (roi * (1 - rib_a) + warped * rib_a).astype(np.uint8)
    # floor drift + shimmer
    bx = xb + (4.0 * np.sin(yb / 33. + 3 * W_ * t) + 2.0 * np.sin(xb / 95. - 2 * W_ * t)).astype(np.float32)
    by = yb + (1.8 * np.sin(xb / 86. + 2 * W_ * t)).astype(np.float32)
    fl = f[fy0:, :]
    wf = cv2.remap(fl, bx, by, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    mix = fl * (1 - floor_a) + wf * floor_a
    shimmer = 0.5 + 0.5 * np.sin(xb / 78. + 2 * W_ * t + np.sin(yb / 33. - 3 * W_ * t))
    mix *= (1 + shimmer[..., None] * 0.05 * (0.6 + 0.4 * math.sin(4 * W_ * t)))
    fl[:] = np.clip(mix, 0, 255).astype(np.uint8)
    # rays
    top = f[:ty1].astype(np.float32)
    top *= 1 + ray_mask * (0.07 * np.sin(xt / 70. + 2 * W_ * t)[..., None] + 0.04 * math.sin(W_ * t))
    f[:ty1] = np.clip(top, 0, 255).astype(np.uint8)
    # bubbles
    layer = np.zeros_like(f)
    for b in bubbles:
        life = (t * b['n'] / T + b['ph']) % 1.0
        x = b['x'] + b['sway'] * math.sin(2 * math.pi * life + b['sp'])
        y = b['y0'] - b['rise'] * life
        if 1110 < x < 1350:          # never across the product body / label
            continue
        a = math.sin(math.pi * life)
        r = max(1, int(round(b['r'])))
        col = tuple(int(c * a) for c in (235, 230, 170))
        cv2.circle(layer, (int(x), int(y)), r, col, 1, cv2.LINE_AA)
        if r > 2:
            cv2.circle(layer, (int(x - r / 3), int(y - r / 3)), 1, tuple(int(255 * a) for _ in range(3)), -1, cv2.LINE_AA)
    f = cv2.addWeighted(f, 1, layer, 0.55, 0)
    # halo tracer (drawn as a fading tail)
    tr = np.zeros_like(f)
    ang = (-96 + 360 * t / T) % 360
    for i in range(10):
        a = (1 - i / 10) ** 1.6
        cv2.ellipse(tr, (CX, CY), (HRX, HRY), 0, ang - (i + 1) * 2.2, ang - i * 2.2,
                    tuple(int(c * a) for c in (255, 246, 200)), 3, cv2.LINE_AA)
    tr = cv2.GaussianBlur(tr, (0, 0), 1.2)
    f = cv2.addWeighted(f, 1, tr, 0.55, 0)
    return f


def encoder(path, w, h, crf):
    cmd = [imageio_ffmpeg.get_ffmpeg_exe(), '-hide_banner', '-loglevel', 'error', '-y',
           '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{w}x{h}', '-r', str(FPS), '-i', '-',
           '-c:v', 'libx264', '-preset', 'slow', '-crf', str(crf), '-profile:v', 'high',
           '-pix_fmt', 'yuv420p', '-g', str(FPS * 2), '-movflags', '+faststart', '-an', str(path)]
    return subprocess.Popen(cmd, stdin=subprocess.PIPE)


OUT.mkdir(parents=True, exist_ok=True)
DESK = (1600, 900)
# phone crop: the product, halo and splash, x 780..1672 of the plate, full height
MX0 = 780
MOB = (720, 760)
desk = encoder(OUT / 'hero-desktop.mp4', *DESK, 25)
mob = encoder(OUT / 'hero-mobile.mp4', *MOB, 25)
for k in range(N):
    fr = frame_at(k / FPS)
    d = cv2.resize(fr, DESK, interpolation=cv2.INTER_AREA)
    m = cv2.resize(fr[:, MX0:], MOB, interpolation=cv2.INTER_AREA)
    desk.stdin.write(d.tobytes()); mob.stdin.write(m.tobytes())
    if k == 0:
        for name, im in (('hero-desktop', d), ('hero-mobile', m)):
            rgb = Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB))
            rgb.save(OUT / f'{name}.jpg', quality=80, optimize=True, progressive=True)
            rgb.save(OUT / f'{name}.webp', quality=74, method=6)
for p in (desk, mob):
    p.stdin.close()
    if p.wait():
        raise SystemExit('ffmpeg failed')
for p in sorted(OUT.iterdir()):
    print(f'{p.name:24s} {p.stat().st_size / 1024:8.0f} KB')
