# 003 — Accessibility & Reduced-Motion Pass

**Written against commit:** `ed3cc16`
**Category:** Accessibility · **Effort:** S–M · **Risk:** S · **Confidence:** High
**Depends on:** nothing (independent).

## Why this matters
Award juries and Lighthouse both score a11y. Two concrete gaps:
1. **`prefers-reduced-motion` is respected in DOM motion** (`reveal.tsx`, `animated-heading.tsx`,
   `char-heading.tsx`, `smooth-scroll.tsx`, `preloader.tsx`, `magnetic.tsx`) **but NOT in the 3D
   canvases** — `grep useReducedMotion components/scene/*` returns nothing. The hero orbit and the
   earth keep spinning for users who asked for no motion (vestibular-trigger risk).
2. The custom cursor (`components/ui/cursor.tsx`) renders a dot+ring but does not hide the native
   cursor, and interactive elements rely on it for affordance; ensure keyboard focus is fully usable
   (the `:focus-visible` gold ring exists in `globals.css` — good; verify nothing sets `outline:none`).

## Files in scope
- `components/scene/hero-canvas.tsx`, `components/scene/os-canvas.tsx` (gate continuous animation)
- `components/hero.tsx`, `components/cleanlines-os.tsx` (pass a `reducedMotion` flag into the canvases)
- `components/ui/cursor.tsx` (respect reduced-motion / coarse pointer; do not trap focus)
- `app/globals.css` (optional: `@media (prefers-reduced-motion: reduce)` hard stop for the `kb-a/kb-b` keyframes and `.grain` already partly covered — verify)

## Files OUT of scope
- All copy, layout, colors. The `prefers-reduced-motion` block already in `globals.css` for `.reveal`.

## Steps
1. **Detect once, pass down.** In `hero.tsx` and `cleanlines-os.tsx`, read `useReducedMotion()`
   (framer-motion) and pass `reduced={reduced}` into `<HeroCanvas reduced/>` / `<OsCanvas reduced/>`.
2. **Gate canvas animation.** In each scene's `useFrame` rotation/float drivers, when `reduced` is
   true: skip the continuous rotation (`Globe` constant spin, hero `VideoCards` ring spin, `Rings`,
   `Dust`, `Float` intensity → 0) and render a static, well-composed frame. Keep video textures
   *playing* (video ≠ vestibular motion) but stop camera/world rotation and the orbit.
   Implementation: guard the `+=` rotation lines with `if (!reduced)`.
3. **Cursor.** In `cursor.tsx`, early-return `null` when `useReducedMotion()` is true OR pointer is
   coarse (it already checks coarse). Confirm it never calls `preventDefault` on focus and is
   `pointer-events: none` (it is). Do **not** add `cursor: none` to the body — keep the native cursor
   for accessibility.
4. **Audit `outline:none`.** `git grep -n "outline" cleanlines-studio` — ensure no component kills the
   focus ring that `:focus-visible` provides. Add `aria-label`s to any icon-only `<button>` missing one
   (e.g. the sound toggle in `sound.tsx` already has one; verify the mute toggle in `reel-cinema.tsx`).
5. **Respect reduced-motion in the preloader curtain** is already done; verify `page-curtain.tsx`
   skips the curtain animation under reduced-motion (it checks `matchMedia` — confirm).

## Verification gate
- `cd cleanlines-studio && npm run build` → 0 errors.
- Manual: Chrome DevTools → Rendering → "Emulate prefers-reduced-motion: reduce". Reload. The earth
  and hero must be **static** (no spin), reveals appear instantly, no curtain animation, native cursor visible.
- Lighthouse (DevTools) Accessibility score should be ≥ 95 on the home route.

## Done criteria
- `git grep -n "reduced" cleanlines-studio/components/scene` shows the guard in both scenes.
- Under emulated reduced-motion, `requestAnimationFrame` rotation deltas are not applied (verify visually: globe does not rotate).
- No `outline: none` without a paired `:focus-visible` style.

## Test plan
Manual reduced-motion emulation + a Lighthouse a11y run. Record the score in `plans/README.md`.

## Maintenance note
Any new `useFrame` animation must accept/check the `reduced` flag. Keep video playback independent of
the motion gate (pausing video on reduced-motion is unnecessary and hurts the brand).

## Escape hatches
- If gating the hero orbit makes the composition look empty/broken when static, **STOP** and instead
  freeze the orbit at a hand-picked rotation (set initial `rotation.y`) rather than removing elements.
