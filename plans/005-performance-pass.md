# 005 — Performance Pass

**Written against commit:** `ed3cc16`
**Category:** Performance · **Effort:** M · **Risk:** M · **Confidence:** Medium-High
**Depends on:** do after 001 (mobile) and 002 (final assets) so you measure the real thing.

## Why this matters
The site ships three.js + R3F + postprocessing + many autoplay videos + 3 HDR earth textures from a
CDN. Decoder exhaustion is already mitigated (`components/ui/in-view.tsx` gates hero/OS canvases;
`media-backdrop.tsx` and `reel-cinema.tsx` pause off-screen video). Remaining wins:
- **No `<link rel="preconnect">`** to the font/CDN/texture origins (`grep poster=` = 0, head has no preconnect).
- **No video `poster`** → black flash before first frame.
- **HDR earth textures** load from `cdn.jsdelivr.net/npm/three-globe/...` at runtime (`os-canvas.tsx`
  `useTexture([...])`) — large, blocking the globe's first paint; could be downscaled / self-hosted.
- Hero/OS three chunks are large; confirm they stay `dynamic({ ssr:false })` (they do) and that
  nothing imports three at the top level of a server component.
- **Dead params**: `Globe({progress, velocity})` in `os-canvas.tsx:219` are unused since rotation went
  constant — remove to cut noise (folds in finding #6).

## Files in scope
- `app/layout.tsx` (add preconnect/dns-prefetch `<link>`s via the `metadata` `other`/`icons` or a
  raw `<head>` in the root layout)
- `components/ui/media-backdrop.tsx`, `components/scene/os-canvas.tsx`, `components/scene/hero-canvas.tsx`
  (poster where applicable; texture sizing; remove dead params)
- `next.config.mjs` (optional: leave as is)

## Files OUT of scope
- Layout/design, copy, the in-view gating logic (already correct).

## Steps
1. **Preconnect.** In the root layout, add `<link rel="preconnect" href="https://cdn.jsdelivr.net" crossOrigin="anonymous" />`
   (earth textures) and a `dns-prefetch`/`preconnect` to the video asset base host used by
   `NEXT_PUBLIC_ASSET_BASE` when set. `next/font` already self-hosts fonts (no Google origin needed).
2. **Earth texture weight.** In `os-canvas.tsx`, the day/night/topology maps are 2K+ JPGs/PNGs from
   jsDelivr. Either (a) self-host a downscaled 1K version under `public/textures/` and load via the
   asset base (better control, CORS-safe), or (b) keep CDN but set `texture.anisotropy` sensibly and
   ensure `Suspense` fallback (the stylized `EarthFallback`) is already in place (it is). Prefer (a)
   if the operator can add the files; otherwise keep (b) and just preconnect.
3. **Poster frames.** For the large DOM background videos (`MediaBackdrop`), add a `poster` (a cheap
   first-frame still) to avoid the black flash, OR keep `preload="none"` (already set) and accept the
   in-view lazy start. Low risk; only add posters if a still is available — do not invent files.
4. **Dead code.** Remove the unused `progress`/`velocity` params from `Globe` in `os-canvas.tsx` (and
   stop passing them if nothing else uses them) — but first confirm with `git grep` they're truly unused
   after constant rotation; the `Rig`/`Nodes`/`useScroll` plumbing in `cleanlines-os.tsx` may still feed
   them. If still wired, leave them and add a `// reserved` comment instead of breaking the chain.
5. **Measure.** Run a production build and a Lighthouse run (mobile) on `/`. Record LCP, TBT, CLS.

## Verification gate
- `cd cleanlines-studio && npm run build` → 0 errors.
- Lighthouse (mobile, `/`): no regression vs. baseline; aim LCP < 4s on throttled mobile (3D sites
  rarely hit green — target "no worse, ideally better"). CLS should be ~0 (videos are absolutely
  positioned backgrounds).

## Done criteria
- `app/layout.tsx` contains the preconnect link(s).
- `npm run build` green; bundle report shows three/R3F still in a **dynamic** (async) chunk, not the
  main entry (check the build output — `/` First Load JS should stay ~140 kB, heavy 3D split out).
- No unused-symbol left from step 4 (or a documented `// reserved`).

## Test plan
Lighthouse before/after, recorded in `plans/README.md`. No unit tests in repo.

## Maintenance note
Keep three.js dynamically imported. New heavy media must go through the in-view gate
(`components/ui/in-view.tsx`) or the `MediaBackdrop` pause pattern, never raw always-on autoplay.

## Escape hatches
- If self-hosting earth textures breaks the WebGL globe (wrong color space / flipped UV), **STOP** and
  revert to the jsDelivr CDN load; the texture URLs are known-good with `access-control-allow-origin: *`.
