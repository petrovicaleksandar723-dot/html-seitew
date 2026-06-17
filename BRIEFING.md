# Creative & Technical Briefing — Cleanlines Studios

**Projekt:** Cleanlines Studios — Content Engine für lokale Marken
**Auftrag:** Bestehende Website radikal auf internationales Award-Niveau heben — nicht neu bauen, sondern in eine immersive Premium-Experience transformieren.
**Stack (bestehend, beibehalten):** Vite · React · TypeScript · React Three Fiber · drei · Three.js · GSAP + ScrollTrigger · Lenis
**Branch:** `claude/ecstatic-brown-erowgd`

---

## 1. Vision & Zielbild

Die Seite soll wirken, als hätte ein Top-Studio sie für **50.000 €+** gebaut. Eine Mischung aus:

- cinematic Creative-Studio-Website
- interaktiver 3D-Web-Experience
- hochwertigem Produkt-/Service-Showcase
- Premium-Agentur-Portfolio
- conversion-starker Landingpage

**Leitsatz:** „Das ist keine normale Website. Das ist eine Marke.“

**Attribute:** mutig · hochwertig · cinematic · interaktiv · sauber typografiert · emotional · performant · verkaufsstark · eigenständig.
**Verboten:** generisch · Template-Look · KI-Baukasten · billige Effekte · Buzzword-Müll.

> Referenzen (Blink Industries, Raven Trading, Studio Pic, Guillaume Colombel) dienen nur als **Prinzipien-Quelle** — keine 1:1-Kopie von Code, Assets oder Layout. Übernommen werden: Qualität, Dramaturgie, Interaktionstiefe, gestalterische Reife.

---

## 2. Design-Direction

**Visuelles System:**

- dunkle Bühne (deep cinematic black)
- weiße Premium-Typografie
- warme/goldene Akzente, kontrolliert (kein Neon, kein billiger Glow)
- subtile Linien & feines Raster
- große Headlines, viel Luft, asymmetrische Layouts
- cinematic Gradients, weiche Glows, feine Noise-Textur
- hochwertige Cards mit Tiefe, Licht, Reflexion

**Design-Tokens (verbindlich):**

```
--black-0:#020202  --black-1:#060504  --black-2:#0d0a07
--gold-1:#f4d7a1   --gold-2:#d6a65f   --gold-3:#8c5a22
--gold-glow:rgba(214,166,95,.28)
--text-main:#f4efe7  --text-soft:rgba(244,239,231,.68)  --text-faint:rgba(244,239,231,.38)
--line-soft:rgba(255,255,255,.1)  --line-gold:rgba(244,215,161,.22)
--page-pad:clamp(36px,5vw,96px)   --max-width:1680px
```

**Regel:** mutig ja — aber immer lesbar, strukturiert, professionell.

---

## 3. Typografie-System

- sehr große Headlines via `clamp()`, aber **nicht gequetscht**
- `text-wrap: balance` auf H1–H3, `text-wrap: pretty` auf Fließtext
- Letter-Spacing-Floor bei großen Headlines: **≥ -0.04em** (keine klebenden Buchstaben)
- `line-height` große Headlines: **0.9 – 1.08**
- Bodytext max. **65–75ch** Zeilenlänge, maximal lesbar
- klare Hierarchie, starke Kontraste, kein Textquetschen, keine kaputten Umbrüche
- Labels klein aber hochwertig (Mono); Zahlen / Kategorien / Steps editorial inszeniert

---

## 4. Layout-System

- Desktop-Content max-width **1440–1680px**, zentriert
- **Ultrawide:** Bühne darf breit sein, **Content bleibt kontrolliert** (nicht auseinandergezogen, keine leeren Flächen)
- **Tablet:** zwei Spalten sauber auf eine reduzieren
- **Mobile:** alles einspaltig, Headlines kleiner, Buttons groß genug, Cards sauber untereinander
- großzügiger vertikaler Section-Abstand, klare Card-Abstände
- **keine** horizontalen Scrollbars, **keine** abgeschnittenen Inhalte, nichts zufällig platziert

---

## 5. Section-Dramaturgie (Brand-Story)

Jede Section = eigene Filmszene mit klarer Funktion: *Aufmerksamkeit → Problem → Wunschzustand → Lösung → Vertrauen → Entscheidung → Anfrage.*

| # | Szene | Funktion | Umsetzung |
|---|-------|----------|-----------|
| 0 | **Preloader** | Spannung aufbauen | Boot-Sequenz, gold Progress, Status-Lines |
| 1 | **Hero** | „Wow“ + Marke | große Headline, Subline, 2 CTAs, Microcopy; 3D-Logo-Centerpiece, Floating-UI-Cards, Lichtlinien, Parallax, Tiefe |
| 2 | **Diagnose / Problem** | Problem sichtbar | Split: links Headline, rechts Diagnose-Panel (Metriken, Statusbars) |
| 3 | **System** | Lösung als System | zentrales Core-Element + orbitierende Module (Premium-„OS“) |
| 4 | **Reel Cinema / Showcase** | Beweis | große Cards mit 01/02/03, Kategorie-Label, Nutzen, Tiefe & Bewegung; echte Videos |
| 5 | **Branchen / Use Cases** | Relevanz | Wechsel-Modul: Branche links, Visual/Beispiel rechts |
| 6 | **Transformation** | Wunschzustand | Vorher/Nachher, cinematic Wipe |
| 7 | **Pipeline / Process** | Klarheit schaffen | Timeline 01–05 mit Scroll-Reveals, Linien, Punkten |
| 8 | **Pakete / Pricing** | Entscheidung | klare Pakete, ein Highlight, gleiche Card-Höhen, CTA + Sicherheits-Microcopy |
| 9 | **Add-ons** | Erweiterung | Premium-Produktzeilen mit Festpreisen |
| 10 | **Trust + FAQ** | Vertrauen | links Headline + Trust-Bullets, rechts ruhiges Accordion |
| 11 | **Final CTA** | Anfrage auslösen | große emotionale Headline, Subline, 2 CTAs, cinematic Glow, Closing-Element |

---

## 6. 3D / Object-Showcase

- Floating Cards, Geräte-Mockups, orbitierende Linien, leuchtende Akzentobjekte, UI-Satelliten
- Tiefenstaffelung über `blur`, `scale`, `opacity`; hochwertige Schatten & Reflexionen
- Details, die beim Scrollen auftauchen — **keine Emojis, keine Standard-Icons**
- Echte 3D (R3F) wo vorhanden; sonst glaubwürdiges **Pseudo-3D mit CSS**: radial gradients, glassmorphism, `transform: perspective()`, layered cards, soft shadows, glow strokes, masked gradients, animated light trails

---

## 7. Motion-Design

- Scroll-Reveal pro Section, staggered Cards, Parallax-Tiefe
- Hover-Tilt **nur subtil**, slow floating objects, glowing lines, smooth transitions
- **Eases:** `ease-out cubic-bezier(0.23,1,0.32,1)` für UI, nie `ease-in`; UI-Animationen < 300 ms
- Press-Feedback auf Buttons (`:active` scale ~0.97)
- keine hektischen Animationen, keine billigen Bounce-Effekte — Motion muss „teuer“ wirken
- Tech: GSAP/ScrollTrigger, Lenis, IntersectionObserver, `requestAnimationFrame` für leichte Parallax; **`prefers-reduced-motion` respektieren**

---

## 8. Performance

- keine unnötigen Libraries / schweren Assets ohne Grund
- Bilder & Videos **lazy-load**, Videos `muted loop playsinline`, `preload=metadata`
- nur GPU-freundliche Properties animieren (`transform`, `opacity`) — kein Layout-Thrashing
- WebGL: Pixel-Ratio gecappt, R3F lazy, ScrollTrigger sauber aufräumen
- Mobile-Performance priorisiert (reduzierte WebGL-Last)
- `npm run build` sauber, `dist/` deploybar, keine Console-Errors

---

## 9. Technische Safety-Regeln (global)

```css
* { box-sizing: border-box; }
html, body { width:100%; overflow-x:hidden; }
img, video, canvas { max-width:100%; }
h1,h2,h3,p,span,li,a,button { overflow-wrap:break-word; }
h1,h2,.headline { text-wrap:balance; }
section { position:relative; overflow:hidden; }
```

---

## 10. Copywriting

**Ton:** premium, klar, selbstbewusst, modern, menschlich, verkaufsstark.
**Nicht:** KI-Floskeln, Buzzwords, lange Absätze, „Wir revolutionieren deine digitale Präsenz…“.
**Sondern:** „Wir machen sichtbar, warum Kunden sich für dich entscheiden sollen.“

- starke Headlines, kurze Subtexte, klare Nutzenkommunikation, CTA-orientiert
- Geschäftsinhalte (Preise, Branchen, FAQ, Kontakt-Logik) bleiben erhalten:
  - Pakete **Starter 250 € · Wachstum 490 € · Premium 890 €** / Monat
  - Add-ons: Website ab 1.400 € · Logo & Branding ab 650 € · Reel-Produktion ab 250 €/Reel · Social-Media-System · Google Business ab 350 €
  - CTAs: „Kostenlos anfragen“ (Mail) · „WhatsApp-Anfrage starten“
  - ⚠️ Platzhalter ersetzen: `cleanlinesstudio@example.com`, `wa.me/49XXXXXXXXXX`

---

## 11. Responsive-Matrix

| Breakpoint | Verhalten |
|------------|-----------|
| Ultrawide (≥1920px) | Bühne breit, Content auf max-width begrenzt, keine leeren Flächen |
| Desktop (1440–1728px) | cinematic, breit, großzügig — die Masterpiece-Ansicht |
| Tablet (≤1080px) | 2 Spalten → 1, Headlines reduziert |
| Mobile (≤640px) | einspaltig, kleinere Headlines, große Buttons, keine Overlaps, keine H-Scrollbar, flüssig |

---

## 12. Quality Gates (Abnahme)

- [ ] keine horizontalen Scrollbars (Desktop / Ultrawide / Mobile)
- [ ] keine Textüberlappung, keine kaputten Umbrüche, keine abgeschnittenen Cards
- [ ] keine leeren / unbalancierten Flächen
- [ ] Navigation, Buttons, CTAs funktionieren; CTA immer sichtbar
- [ ] Hero passt in den ersten Viewport, Headline ≤ 3 Zeilen (Desktop)
- [ ] Pakete: gleiche Card-Höhen, ein Highlight, CTA pro Paket
- [ ] Animationen flüssig, `prefers-reduced-motion` respektiert
- [ ] `npm run build` ohne Fehler, keine Console-Errors, alle Videos vorhanden
- [ ] Mobile / Desktop / Ultrawide je visuell geprüft (Screenshots)
- [ ] Design wirkt hochwertig, eigenständig, nicht generisch

---

## 13. Vorgehen (Reihenfolge)

1. Globale Safety-CSS + Typo-/Motion-Tokens härten
2. Hero-Komposition auf „Wow“ schärfen (3D-Logo, Floating-Cards, Parallax, Microcopy)
3. Section für Section als Szene veredeln (Reveal, Tiefe, Pseudo-3D, Spacing)
4. Multi-Viewport-QA (Desktop / Ultrawide / Mobile) mit Screenshots → Fehler fixen
5. Performance-Check + finaler Build + `dist`
6. Selbst-Review gegen die Quality Gates, dann Übergabe

---

*Dieses Briefing ist die verbindliche Grundlage für den Award-Pass. Jede Entscheidung wird daran gemessen: hochwertig, eigenständig, conversion-stark — nicht nur „schöner“.*
