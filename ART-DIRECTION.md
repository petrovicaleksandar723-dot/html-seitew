# Cleanlines Studio — Art Direction & Build (landing.html)

Premium cinematic 3D landing page. Inspired by the *quality level* of le-lab.io,
lejardin.pha5e.com, spacers.wannathis.one — principles extracted, **nothing copied**.

## 1. Design DNA
- One curated world, not a template: deep black canvas, a single luminous gold hero object.
- Restraint + cinema: few but strong moments, generous negative space, editorial type.
- Brand-driven 3D (the CleanLines hexagon), never random blobs.

## 2. Color world
- Base: near-black `#060608` / `#0c0c11`.
- Accent: gold `#c9a25a` → `#e8d2a0` → highlight `#fff4da`.
- Text: warm ivory `#f5f1ea`, muted `#a9afba`. Cold purple only as faint aura depth.

## 3. Typography hierarchy
- Display: **Sora** 800, oversized (clamp 44→96px), tight tracking, per-word reveal.
- Body: **Inter**, 16px+ on mobile, 1.6 line-height, ≤60ch measure.
- Marquee: outlined (text-stroke) giant Sora — kinetic texture band.

## 4. 3D asset concept (procedural — no GLB needed)
- Extruded, bevelled **gold hexagon ring** (the brand mark) + inner icosahedron core.
- Gold "dust" particle field (additive) for parallax depth.
- Cinematic 3-point light: warm key, gold rim, soft fill + exponential fog.

## 5. Scroll choreography
- Hero 0–100%: hexagon rotates, core counter-rotates, camera dollies in (z 9→12),
  object drifts down, gold dust parallaxes. Pointer adds subtle camera look-around.
- Each section: entrance reveal (rise + fade, staggered), gold gradient card borders ignite.
- Showreel & industries: native side-by-side swipe rails (no scroll-jacking).

## 6. Interaction moments
- Tap a reel phone → immersive fullscreen player (sound on).
- Hover: magnetic buttons, cursor glow, card tilt/edge-glow (desktop).
- Sticky glass header w/ scrollspy, scroll progress bar, sticky mobile CTA dock.

## 7. Mobile simplification
- Particle count + DPR reduced; grid overlay & cursor glow disabled on touch.
- 3D auto-pauses off-screen; `prefers-reduced-motion` disables 3D + animation.
- Single-column, ≥48px touch targets, no horizontal overflow.

## 8. Performance budget
- Three.js vendored locally (1 file, no CDN), DPR capped (≤1.5 mobile / ≤2 desktop).
- rAF render only while hero in view + tab visible. Lazy videos: only visible reel plays.
- **Guarded fallback**: no WebGL / weak phone / load error → cinematic CSS hero stays.

## Conversion (premium-local-business-converter)
Hero offer → marquee → deliverables → showreel → "für wen" (all local businesses) →
3-step process → before/after → free preview → packages → FAQ → final CTA (mail + WhatsApp).
Copy speaks to owners (more attention, trust, bookings); no buzzword spam. No payment on site.

## QA note
Built defensively to the performance-mobile-qa checklist. Live browser/Playwright QA
could not run inside this cloud container (no GPU/sandbox for Chromium); run locally with
the project's Playwright setup, or just deploy and view — the 3D renders in any real browser.
