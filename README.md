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
- **Accessibility:** continuous loop, no pause button (Jeff, 2026-11-04); video is `aria-hidden`;
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

## Logo marquee (#arlm)

The client-logo strip directly under the hero, rebuilt 2026-11-03 to replace the template marquee
(Section 3). That strip had three problems:
- Its third group was template placeholder logos.
- Its groups scrolled at three different speeds, so logos overlapped and the loop jumped.
- Its logos were 1x PNGs, several of them stretched.

| File | Role |
|---|---|
| `AquaRev_Logo_Marquee.html` | Master: label, the 13-logo list (order, per-logo `--h` height, alt text), CSS and JS. |
| `build-marquee.sh` | Generates `logo-marquee.css/js`, `webflow-embed-logo-marquee.html`, `preview-marquee.html` (hero + strip). |
| `logos/` | White-on-transparent marks made by `src/make_logos.py` from `Assets/Client Logos` (SVG where the vector was clean, 2x PNG knock-outs for boxed logos). |

**How it works**
- **Loop:** the script clones the list once (`aria-hidden`, empty alt), and CSS slides the track exactly
  −50%, so the loop is seamless at any width.
- **Speed:** the duration is set from the list width, so the speed is a constant 34 px/s on every screen.
- **Continuous by design (Jeff, 2026-11-03):** no label, no pause button, no hover pause. It only idles
  while off screen, where nobody can see it.
- **Reduced motion:** visitors with *reduce motion* on, or without JS, get a static, centred, wrapping row.

**Changing logos**
1. Add or replace the source in `src/make_logos.py`.
2. Add an `<li>` with `--h` and the file's width/height in the master. Optical rule: h = √(4000 / aspect),
   26–52 px.
3. Run `./build-marquee.sh`, push, and replace the code of embed `af25d348…`.

**Webflow:** page-level HtmlEmbed `af25d348-0a33-11c3-5972-565137cabd3d`, directly after the hero embed.
The old **Section 3** is hidden, not deleted.

## Features section (#arfx)

"Hotels / Resorts & Commercial Operators Advantage", the section under the logo banner, replacing
Webflow Section 7 (2026-11-04). Master `AquaRev_Features.html`, build `build-features.sh` →
`features.css/js`, `webflow-embed-features.html`, `preview-features.html` (hero + banner + section).

- **Order:** product introduction (two paragraphs), then "Average Consumption & Cost Reductions" (nine
  figures in a 3×3 grid, one cyan gradient), then the Case Studies feature link, then three one-line
  value cards (/solution, /specifications, /certificationmap), then the ROI Assessment CTA and "See the
  lab data" (/data).
- **Figures:** IAPMO R&T lab (41% chlorine, 36% chloramines, 23% evaporation) and Turtle Bay field data
  (64% chemical spend, 70% replacement water, 50% bicarbonate, 43% acid, 30% salt, 20% pump energy).
  Each tile carries a source tag. No on-page sources note (removed at Jeff's request).
- **Count-up:** runs once on scroll and always lands on the real number. Reduced-motion visitors see the
  final values.
- **Webflow:** page-level embed directly after the logo-banner embed. Section 7 is hidden, not deleted.

## Where it lives in Webflow (home page)

Installed 2026-11-03 through the Webflow connector:

- **Live embed:** page-level HtmlEmbed `797c463a-9858-5a88-c884-8f7a8fb09e87` on Home
  (`691fa5d73fc3a5a75a65f012`), a direct child of the body between the hidden **Hero 1** component
  and Section 3. Webflow won't place elements beside a component instance, so it sits after Hero 1
  instead of before it. The result is the same because Hero 1 is hidden.
- **Old hero:** the Hero 1 component's root section (`Hero Home`) is hidden, so the page has one H1. An
  empty embed (`864f6816…`) was added inside that hidden section during setup. It renders nothing and can
  be deleted.
- **Copy changes:** rebuild, then replace the code of embed `797c463a…` with
  `webflow-embed-home-hero.html` (paste it, or ask Claude to set it through the connector), and publish.
