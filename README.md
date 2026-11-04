# AquaRev home page hero — Deployment

Hero section for **www.aquarevwater.us** (home page), built from the approved motion concept in
`Marketing/Website/Assets/Motion Graphics/aquarev-updated-motion-package/`. Every style is scoped under
`#arhh`; CSS, JS, video, posters and badges are hosted on GitHub Pages
(`jeffatley-web/aquarev_home_hero`).

Unlike the other site pages, the hero's **markup is pasted into Webflow** (not injected by JS), so the H1,
copy and CTA are in the page HTML for search engines and paint before any script runs.

| Change | What to do |
|---|---|
| Styling, animation, video behaviour | Edit master → `./build.sh` → push. No Webflow change. |
| Copy, links, badges (markup) | Edit master → `./build.sh` → push → re-paste the embed. |
| Video or poster | Re-run `src/` scripts (below) → `./build.sh` → push. |

## What it does

- **Copy:** eyebrow, a single H1 ("Cleaner Water. Reduced Costs. Lifetime Warranty."), the subhead from the
  concept, **Get Your ROI Assessment** → `/contact` (same target as the nav button), "See case studies" →
  `/case-studies`, badge row (IAPMO, NSF, WQA, BBB, Made in USA, Lifetime Warranty) and the line
  "Component certified to NSF/ANSI/CAN 50 via IAPMO."
- **Desktop (≥ 900 px):** one screen tall below the sticky nav (measured at runtime, 560–920 px). The
  16:9 video is anchored right and never cropped top or bottom; a left scrim keeps the copy readable.
- **Phones and portrait tablets (< 900 px):** product video on top (a separate 720×760 crop), copy below,
  full-width CTA under 560 px. Checked at 375×667 (CTA above the fold), 390×844, 768×1024, 844×390.
- **Video:** silent 12 s seamless loop. Starts only after the page has loaded, pauses when scrolled away or
  the tab is hidden, swaps desktop/mobile files at the breakpoint, and fades in over a poster that is the
  exact first frame. Not loaded at all with *reduce motion* turned on or *Data Saver* / 2G; the poster
  shows instead.
- **Accessibility:** pause/play button (WCAG 2.2.2), remembered per visitor; video is `aria-hidden`;
  logos have alt text; visible focus rings; entrance and CTA-sheen animations only run when motion is
  welcome; text contrast on navy is well above AA.

## Files

| File | Role |
|---|---|
| `AquaRev_Home_Hero.html` | Master. The only file you edit (Edit tool only, never regenerate it with a script). Opens on its own in a browser. |
| `build.sh` | Generates everything below from the master. |
| `home-hero.css`, `home-hero.js` | Generated. Hosted on GitHub Pages. |
| `webflow-embed-home-hero.html` | Generated. Paste into the Webflow Embed (see below). |
| `preview.html` | Generated. Local mirror of the embed with a stand-in sticky nav. |
| `media/hero-desktop.mp4/.jpg/.webp` | 1600×900 loop (1.8 MB) + first-frame posters. |
| `media/hero-mobile.mp4/.jpg/.webp` | 720×760 product crop (1.2 MB) + posters. |
| `img/*.png` | Badges trimmed from `Marketing/Website/Assets` at 2× display size. |
| `src/make_plate.py` | Removes the baked-in text, CTA and logos from `src/concept.png` → `src/plate.png`. |
| `src/render_loop.py` | Animates the plate (water, bubbles, halo tracer, light rays) → `media/`. |
| `src/make_badges.py` | Trims the badge PNGs → `img/`. |

Rebuilding media needs Python with `opencv-python-headless numpy imageio-ffmpeg pillow`:

```
python src/make_plate.py src/concept.png src/plate.png
python src/render_loop.py src/plate.png media
python src/make_badges.py "../Assets" img
```

## Installing in Webflow (home page)

1. In the Designer, select the old hero section (`section.hero-home`, the water video with three H1s).
2. Add an **Embed** element directly above it, as a child of the page body (not inside a container, so it
   runs full width), and paste the whole of `webflow-embed-home-hero.html`.
3. Hide or delete `section.hero-home`, so the page has one H1.
4. Publish when ready.
