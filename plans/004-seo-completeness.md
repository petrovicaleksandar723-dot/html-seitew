# 004 — SEO & Metadata Completeness

**Written against commit:** `ed3cc16`
**Category:** SEO · **Effort:** S · **Risk:** S · **Confidence:** High
**Depends on:** nothing (independent). Quick win.

## Why this matters
`app/layout.tsx` has good base metadata + OpenGraph text, but the route is missing the files that
make a site share-ready and crawlable. Confirmed missing (all return MISSING):
`app/opengraph-image.(tsx|png)`, `app/sitemap.ts`, `app/robots.ts`, `app/manifest.ts`,
`app/not-found.tsx`. No JSON-LD structured data. `metadataBase` is a placeholder
(`new URL("https://cleanlines.studio")`, `layout.tsx:38`).

## Files in scope (all NEW unless noted)
- `app/opengraph-image.tsx` (dynamic OG image via `next/og` `ImageResponse`, 1200×630, brand look)
- `app/icon.svg` already exists (favicon) — keep.
- `app/sitemap.ts`, `app/robots.ts`, `app/manifest.ts`, `app/not-found.tsx`
- `app/layout.tsx` (MODIFY: confirm/raise `metadataBase` to the real domain when known; add a JSON-LD
  `<script type="application/ld+json">` Organization block in the body, or via a metadata `other` field)

## Files OUT of scope
- Components, 3D, styles. Do not change existing `metadata` copy — only add.

## Steps
1. **OG image.** Create `app/opengraph-image.tsx` exporting `size = {width:1200,height:630}`,
   `contentType = "image/png"`, and a default async component returning `new ImageResponse(<div …>)`
   with black bg, the gold hex mark (inline SVG/JSX), "CLEANLINES STUDIOS", and the tagline
   "Dein Betrieb. Sichtbar wie eine große Marke." Use `next/og`. No external fonts required (system
   is fine inside ImageResponse, or load Hanken via fetch if the executor wants exact brand type).
2. **robots.ts** → allow all, point `sitemap` at `${metadataBase}/sitemap.xml`.
3. **sitemap.ts** → one entry for `/` with `lastModified: new Date()`, `changeFrequency: "monthly"`, `priority: 1`.
4. **manifest.ts** → name "Cleanlines Studio", short_name "Cleanlines", `theme_color:"#050505"`,
   `background_color:"#050505"`, icons referencing `icon.svg`, `display:"standalone"`.
5. **not-found.tsx** → a small branded 404 (black bg, gold hex mark, "Seite nicht gefunden",
   a link back to `/`). Mark it a Server Component (no "use client" needed).
6. **JSON-LD.** Add an Organization + WebSite schema. Simplest: in `layout.tsx`, render a
   `<script type="application/ld+json" dangerouslySetInnerHTML={{__html: JSON.stringify(schema)}} />`
   inside `<body>` (Server Component context). Include name, url, logo, sameAs (empty array ok), description.
7. **metadataBase.** If the real production domain is known, set it; otherwise leave the placeholder
   but add a `// TODO: set real domain` comment. Note: the **static-export preview** ignores most of
   this (it's for the deployed Vercel build) — that's expected; these files cost nothing in export.

## Verification gate
- `cd cleanlines-studio && npm run build` → 0 errors, and the build log should now list the new
  routes (`/opengraph-image`, `/sitemap.xml`, `/robots.txt`, `/manifest.webmanifest`, `/_not-found`).
- `npx tsc --noEmit` clean.
- Manual: `npm run dev`, visit `/opengraph-image` (renders the PNG), `/robots.txt`, `/sitemap.xml`,
  `/manifest.webmanifest`, and a bad URL (shows the branded 404). View source of `/` → JSON-LD present.

## Done criteria
- `ls app/{opengraph-image.tsx,sitemap.ts,robots.ts,manifest.ts,not-found.tsx}` all exist.
- Build output enumerates the new SEO routes.
- `/` HTML contains `application/ld+json`.

## Test plan
Manual route checks above + paste the deployed URL into a social-preview validator after the next
Vercel deploy (out of scope for the executor; note it for the operator).

## Maintenance note
When the real domain is live, update `metadataBase` and the manifest `start_url`. The `next/og` route
must stay Edge-compatible (no node-only APIs) if deployed on Edge.

## Escape hatches
- If `next/og` `ImageResponse` fails to build in the static-export path, gate `opengraph-image.tsx`
  with `export const dynamic = "force-static"` and a static fallback PNG in `app/`; STOP and report if
  it still fails the export build.
