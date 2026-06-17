# Cleanlines Studio — Content Engine

An award-level creative-development experience for **Cleanlines Studio**:
cinematic Reels, AI visuals and content systems for local businesses that want
to look like a real brand online.

Built as a full creative app — not a static page.

## Stack

- **Vite** + **React** + **TypeScript**
- **React Three Fiber** / **drei** / **Three.js** — WebGL content engine
- **GSAP** + **ScrollTrigger** — cinematic, scroll-driven motion
- **Lenis** — smooth scroll
- **lucide-react** — icons

## Experience structure (12 scenes)

1. Preloader — premium boot loader
2. Hero / WebGL Content Engine — glass core, torus rings, floating reel planes, particles
3. Diagnosis Dashboard — animated meters + scan grid
4. Content Operating System — central core with connected, activating modules
5. Reel Cinema — pinned horizontal scroll, cinematic active reel, real videos
6. Industries Editorial Gallery — huge type list ↔ large visual stage
7. Before/After Transformation — pinned gold clip-path wipe
8. Production Pipeline — gold signal travels the rail, lighting each step
9. Packages — 3D glass/metal premium tiers
10. Add-ons / Einzelaufträge — premium product rows
11. Trust + FAQ — trust protocol + accordion
12. Final Cinematic CTA — `final.mp4` light wall + contact actions

## Develop

```bash
npm install
npm run dev      # http://localhost:5173
```

## Build

```bash
npm run build    # type-checks, then builds to /dist
npm run preview  # serve the production build locally
```

## Deploy (Netlify)

`netlify.toml` is configured:

```toml
[build]
  command = "npm run build"
  publish = "dist"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

Connect the repo in Netlify (or drag the `dist/` folder to
https://app.netlify.com/drop). Videos in `public/assets/videos/` ship as-is and
are long-cached via the headers rule.

## Content & contact configuration

All business content (German copy, prices, industries, FAQ, packages, add-ons)
lives in a single source of truth: [`src/content/siteContent.ts`](src/content/siteContent.ts).

⚠️ Before going live, replace the placeholder contact details at the top of that
file (kept from the original site):

```ts
export const contact = {
  email: "cleanlinesstudio@example.com", // TODO: real email
  whatsappNumber: "49XXXXXXXXXX",        // TODO: real WhatsApp number (49..., no +)
  location: "München / Remote",
};
```

`mailto:` and WhatsApp (`wa.me`) links are generated from these values.

## Prices (preserved from the live site)

- **Starter** — 250 € / Monat
- **Wachstum** — 490 € / Monat (Beliebt)
- **Premium** — 890 € / Monat

Add-ons: Website-Design ab 1.490 € · Logo & Branding ab 590 € ·
Reel-Produktion ab 290 € / Reel · Social-Media-Setup ab 390 €.
