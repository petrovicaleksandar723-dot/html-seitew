# 001 — Responsive / Mobile Overhaul

**Written against commit:** `ed3cc16`
**Category:** Design / Correctness · **Effort:** L · **Risk:** M · **Confidence:** High
**Depends on:** nothing. Do this first.

## Why this matters
Awwwards/FWA juries open the site on a phone first. Several sections are desktop-only and
break below `lg` (1024px):
- `components/scene/os-canvas.tsx`: the whole earth group is rendered at world X `+2.7`
  (`<group position={[2.7, 0, 0]}>` inside `OsCanvas`), tuned so the globe sits right of the
  desktop text column. On a 390px phone the globe is pushed mostly off the right edge.
- `components/cleanlines-os.tsx`: content is a single `max-w-[560px]` left block; on mobile it
  overlaps the off-screen globe and the phones clip.
- Horizontal pinned galleries (`components/reel-cinema.tsx` `HorizontalReels`,
  `components/pipeline.tsx` `PinnedTimeline`) only fall back to a scroll row under
  `useReducedMotion`; on a normal phone they still try to pin + translateX, which is janky on touch.
- Most section grids jump straight from 1 column to `lg:grid-cols-*` with no `sm:`/`md:` step.

## Files in scope
- `components/scene/os-canvas.tsx` (add a responsive `offsetX` prop)
- `components/cleanlines-os.tsx` (compute offset; stack on mobile)
- `components/reel-cinema.tsx` (treat small screens like reduced-motion: scroll row)
- `components/pipeline.tsx` (same)
- `components/hero.tsx` (verify logo/cards not clipped on mobile; tune camera/scale only if needed)
- Section grids: `industries.tsx`, `services.tsx`, `content-compare.tsx`, `pricing.tsx`, `diagnosis.tsx`, `faq.tsx` — add `sm:`/`md:` steps where a 1→3 jump exists.

## Files explicitly OUT of scope
- `lib/`, `app/layout.tsx`, `next.config.mjs`, `app/globals.css` reset block.
- Do not touch the gold color tokens or fonts.

## Current-state excerpts
`components/scene/os-canvas.tsx` (OsCanvas return, ~line 270):
```tsx
<group position={[2.7, 0, 0]}>
  <Rig>
    <Globe progress={progress} velocity={velocity} />
  </Rig>
</group>
```
`components/cleanlines-os.tsx` (~line 43): `<section … className="relative flex min-h-screen items-center overflow-hidden bg-black …">` then a `<div className="shell content relative z-10"><div className="max-w-[560px]">…`.

## Steps (ordered)
1. **OsCanvas offset prop.** Add `offsetX?: number` to `OsCanvas`’s props (default `2.7`). Replace the hard-coded `position={[2.7, 0, 0]}` with `position={[offsetX, 0, 0]}`. Also widen camera FOV slightly on small offset so a centered globe fits.
2. **Drive offset from `cleanlines-os.tsx`.** Add a `useState`+`useEffect` that reads `window.matchMedia("(min-width: 1024px)")` (guard for SSR; default desktop). Pass `offsetX={isDesktop ? 2.7 : 0}` to `<OsCanvas>`. When not desktop: change the content wrapper from a left `max-w-[560px]` block to a centered column that sits *below* the globe — e.g. on mobile the layout becomes: globe canvas as a ~50vh top band, then the heading + module cards stacked full-width beneath. Use `lg:` to keep the current desktop layout unchanged.
3. **Module grid mobile.** The 6 OS module cards currently `grid sm:grid-cols-2`; confirm they read on a 390px screen (single column, `bg-bg/75 backdrop-blur-xl` already there). Keep.
4. **Reel-cinema + pipeline mobile fallback.** In `HorizontalReels` and `PinnedTimeline`, broaden the existing `if (reduce)` early-return to also trigger on small screens: add a `const [mobile, setMobile] = useState(false)` set from `matchMedia("(max-width: 1023px)")`, and use `if (reduce || mobile)` to render the simple horizontal-scroll row (`overflow-x-auto`, snap optional) instead of the pinned translateX. This removes touch jank.
5. **Grid steps.** For `industries.tsx`, `services.tsx`, `content-compare.tsx`, `pricing.tsx`, add `sm:grid-cols-2` before the `lg:grid-cols-3` where applicable; verify `diagnosis.tsx` two-column panel stacks cleanly (`lg:grid-cols-[…]` → single column below lg, already true — just confirm gauge + sparkline don’t overflow at 360px).
6. **Hero check.** At 390px, confirm the 3D logo isn’t clipped and the headline doesn’t collide with the canvas. The headline is `pointer-events-none` over the canvas already. If the logo is too large, pass a smaller `scale` on mobile via a matchMedia prop on `HeroCanvas` (mirror the OsCanvas offset pattern) — only if visibly clipped.

## Verification gate
- `cd cleanlines-studio && npm run build` → must compile + generate pages with no errors.
- Manual: run `npm run dev`, open DevTools device toolbar at **390×844 (iPhone)** and **768×1024 (iPad)**. Confirm: no horizontal scrollbar (the global `overflow-x:hidden` is in `globals.css`), globe visible/centered on mobile, OS text readable beneath it, reel + pipeline scroll horizontally by drag without pinning jank, every section single-column and legible.

## Done criteria (machine/observable)
- `npm run build` exits 0.
- No element produces horizontal overflow at 390px (check `document.documentElement.scrollWidth === window.innerWidth` in console).
- `cleanlines-os.tsx` passes a non-2.7 offset to `OsCanvas` below 1024px (grep shows `offsetX`).

## Test plan
No unit tests in repo. Add a short note to `plans/README.md` status. Manual responsive QA is the test; record the three breakpoints checked.

## Maintenance note
Future 3D tweaks must keep the `offsetX` prop responsive. Any new pinned-scroll section must include the `reduce || mobile` fallback from step 4.

## Escape hatches
- If centering the globe on mobile makes the orbiting phones overlap the stacked text, **STOP** and reduce the phone orbit radius (`R + 0.75` in `os-canvas.tsx`) on mobile only, rather than fighting it with z-index.
- If `matchMedia` causes a hydration mismatch warning, initialize state to the desktop value and update in `useEffect` (never read `window` during render).
