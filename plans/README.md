# Cleanlines Studio — Award-Winning Upgrade Plans

Audit by Fable-skill (advisor). Target: elevate the `cleanlines-studio/` Next.js + WebGL
site to Awwwards/FWA-level maximum. All plans are written against commit `ed3cc16`.

**Project facts (every plan assumes these):**
- Next.js 14.2.35 (App Router) + TypeScript + Tailwind, in `cleanlines-studio/`.
- Motion: framer-motion 11, lenis. 3D: three 0.164 + @react-three/fiber 8.16 + drei 9.105 + @react-three/postprocessing.
- No tests, no ESLint config, no CI. **Verification gate = `cd cleanlines-studio && npm run build`** (runs the TS type-check; must stay green). Optionally `npx tsc --noEmit`.
- Preview is a static export driven by env vars `BUILD_EXPORT=1 ASSET_PREFIX=… NEXT_PUBLIC_ASSET_BASE=…` (see `next.config.mjs`, `lib/asset.ts`). Normal `npm run build` is the gate; do not change the export mechanism unless a plan says so.
- Brand system: deep black `#050505`/`#0a0a0c`, champagne gold `#d8b274`/`#f4d79e`/`#a87f3e`; fonts via `next/font` (Hanken Grotesk display, DM Sans body, Instrument Serif italic accent, JetBrains Mono labels). Match this in any new UI.

## Recommended execution order & dependencies

| Order | Plan | Depends on | Leverage |
|---|---|---|---|
| 1 | `001-responsive-mobile-overhaul.md` | — | High (foundational; award juries test mobile first) |
| 2 | `003-a11y-reduced-motion.md` | — (independent) | Medium-High |
| 3 | `004-seo-completeness.md` | — (independent) | Medium |
| 4 | `002-brand-broll-integration.md` | brand assets exist in `public/videos/` | High (perceived quality) |
| 5 | `005-performance-pass.md` | after 001/002 (measure final) | Medium-High |

`006` (dead 3D params cleanup) is folded into 001/005 as a sub-step; not worth a standalone plan.

## Status

| Plan | Status |
|---|---|
| 001-responsive-mobile-overhaul | TODO |
| 002-brand-broll-integration | TODO |
| 003-a11y-reduced-motion | TODO |
| 004-seo-completeness | TODO |
| 005-performance-pass | TODO |

## Considered and rejected
- *Rewrite 3D in raw WebGL / add path tracing* — not feasible with animated video textures + scroll in-browser; current R3F + HDR IBL + bloom is the correct approach. Rejected.
- *Drop the preloader* — it is brand-on and now fail-safe (`preloader.tsx` 4.5s timeout); keep.
