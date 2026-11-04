import sys, cv2, numpy as np
src, out = sys.argv[1], sys.argv[2]
img = cv2.imread(src).astype(np.float32)
H, W = img.shape[:2]
def ramp(a, lo, hi): return np.clip((a - lo) / (hi - lo), 0, 1)
# 1) headline, subhead and CTA: replace with the left-edge water colour carried across each row,
#    then fade back into the original artwork toward the splash on the right
edge = cv2.GaussianBlur(np.percentile(img[:, 0:1000], 30, axis=1, keepdims=True), (0, 0), 14)   # H x 1 x 3, row background tone (30th pct ignores text)
fill = np.repeat(edge, W, axis=1)
fill = cv2.GaussianBlur(fill, (0, 0), 3) + np.random.default_rng(3).normal(0, 1.1, fill.shape)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
a = ramp(yy, 40, 108) * (1 - ramp(yy, 650, 700))                     # rows: eyebrow .. CTA
a *= np.where(yy < 545, 1 - ramp(xx, 884, 960), 1 - ramp(xx, 680, 900))  # cols: text block / CTA
a *= ramp(xx, 0, 84)
a = a[..., None]
res = img * (1 - a) + fill * a
# 2) badge row on the caustic floor: lay in compressed floor texture from the clean band below
y1, y2, x1, x2 = 660, 806, 40, 1070
donor = cv2.resize(res[808:941, x1:x2], (x2 - x1, y2 - y1), interpolation=cv2.INTER_AREA)
tex = res.copy(); tex[y1:y2, x1:x2] = donor
b = ramp(yy, 664, 696) * (1 - ramp(yy, 796, 808)) * ramp(xx, 40, 92) * (1 - ramp(xx, 1028, 1068))
b = b[..., None]
res = res * (1 - b) + tex * b
cv2.imwrite(out, np.clip(res, 0, 255).astype(np.uint8))
