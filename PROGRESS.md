# PROGRESS — Cleanlines Studios EDITORIAL LUXURY rebuild (Fable Mode)

Direction chosen by user: **Editorial Luxury** (Musée de la Plaisance vibe) —
light ivory paper canvas, deep warm ink typography, elegant SERIF display
headlines + clean grotesk, huge cinematic media, generous whitespace, slow
refined transitions, alternating light/dark scenes. Accent: **warm gold** kept.
Desktop-first (mobile secondary). Copy/prices/videos/contact preserved.

## Stages
- [x] A. Fonts (Fraunces serif + Hanken Grotesk) + editorial token system
- [x] B. Global base flips to paper/ink; selection, cursor, grain tuned for light
- [x] C. Rebuild HERO: serif headline + large cinematic video, editorial layout
        (retire the dark WebGL engine / iPad-dashboard look)
- [x] D. Reskin all sections to editorial: light scenes + intentional dark
        scenes for Reel Cinema & Final CTA (drama). Flip glass cards to paper/ink.
- [x] E. Motion: refined slow reveals, serif mask reveals, keep Lenis/GSAP
- [x] F. Build + desktop screenshot verification of every scene; iterate

## Notes
- Token strategy: redefine existing CSS vars to editorial values (flips bulk),
  add --noir-* for dark scenes, override glassy cards individually.
- --font-display = Fraunces (serif), --font-mono = Hanken Grotesk (tracked labels)

## Evidence log
(append tool-proven results)

## Result (verified)
Full Editorial Luxury rebuild shipped: ivory paper canvas, Fraunces serif
display, deep ink + warm gold, alternating light scenes with dark cinematic
Reel Cinema + Final CTA. New serif media hero (dark WebGL engine retired).
Screenshot-verified hero, diagnosis, OS, reel cinema, industries, transformation,
packages, final, footer. 0 horizontal overflow + 0 page errors on ultrawide/desktop/mobile.

## v2 — Next.js award stack migration (verified)
Migrated Vite → Next.js 14 (App Router, static export `out/`). Stack now:
Next.js + TypeScript + Tailwind (preflight off, coexists w/ design system) +
GSAP + ScrollTrigger + SplitText (gsap 3.15) + Lenis + Three/R3F/Drei/postprocessing
+ next/font (Fraunces + Hanken Grotesk). Hero 3D loaded client-only (ssr:false)
with Higgsfield GLB (runtime) + procedural fallback. `next build` green,
static export renders, 0 page errors, headline SplitText reveals working.
Deploy: Netlify (publish `out`) / Vercel / drag `out/` to netlify drop.

## v2.1 — real cinematic asset + scroll choreography (no zip)
- Higgsfield: generated a cinematic 16:9 luxury film (image -> veo3_1_lite,
  1080p, 8s) and wired it as the Final CTA background (runtime URL + local
  fallback). ~56 credits left.
- Added a depth-parallax engine (data-parallax, scrubbed) on diagnosis panel,
  industries stage and final video; reduced-motion aware.
- Verified static export: 0 overflow desktop/mobile, 0 page errors.
