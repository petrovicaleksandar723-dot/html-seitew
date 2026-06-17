# Cleanlines Studio — Award-Level Website

Cinematic premium website for **Cleanlines Studio**, a content studio for local
businesses. Built as a real production Next.js app with WebGL 3D.

## Stack

- **Next.js 14** (App Router) + **TypeScript**
- **Tailwind CSS** design system (cinematic black + champagne gold)
- **React Three Fiber / three.js** + **@react-three/postprocessing** (Bloom) — real WebGL hero & "Cleanlines OS" scenes
- **Framer Motion** — reveals, accordion, magnetic buttons, scroll-linked timeline
- **Lenis** — smooth inertial scroll
- `next/font` (Hanken Grotesk, DM Sans, Instrument Serif, Geist Mono) — no external font CDN

## Run locally

```bash
npm install
npm run dev      # http://localhost:3000
npm run build    # production build
npm start        # serve the build
```

## Deploy to Vercel

1. Push this repo to GitHub.
2. In Vercel: **New Project → Import** the repo.
3. Set **Root Directory** to `cleanlines-studio`.
4. Framework preset is auto-detected (Next.js). Deploy.

The WebGL canvases are dynamically imported with `ssr: false` and ship with
CSS-glow fallbacks, so there are no hydration errors and no blank canvas if
WebGL is unavailable.

## Structure

```
app/            layout, page, global styles + metadata/OG
components/      one file per section (hero, diagnosis, … final-cta)
components/ui/   reveal, magnetic button
components/scene/ hero-canvas, os-canvas (R3F / WebGL)
lib/constants.ts all section copy & data
```
