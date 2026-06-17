"use client";

import { Reveal } from "@/components/ui/reveal";
import { ParallaxImage } from "@/components/ui/parallax-image";
import { IMG } from "@/lib/content";

export function Manifesto() {
  return (
    <section className="relative py-[clamp(90px,16vw,200px)]">
      <div
        className="shell grid items-center gap-12 lg:grid-cols-[1.05fr_0.95fr] lg:gap-20"
        style={{ ["--max" as string]: "1280px" }}
      >
        <div className="order-2 lg:order-1">
          <Reveal>
            <span className="eyebrow">Warum wir</span>
          </Reveal>
          <Reveal delay={0.05}>
            <h2 className="mt-6 font-display text-[clamp(30px,4.6vw,60px)] font-bold leading-[1.04] tracking-[-0.02em]">
              Du lieferst jeden Tag starke Arbeit.{" "}
              <span className="font-serif italic text-gold">
                Online sieht man das oft nicht.
              </span>
            </h2>
          </Reveal>
          <Reveal delay={0.12}>
            <p className="mt-7 max-w-[520px] font-body text-[clamp(15px,1.5vw,18px)] leading-relaxed text-dim">
              Genau das ändern wir. Wir machen sichtbar, warum Kunden sich für
              dich entscheiden — mit Content, der Vertrauen schafft, professionell
              aussieht und deine Leistung klar auf den Punkt bringt.
            </p>
          </Reveal>

          <div className="mt-10 grid max-w-[460px] grid-cols-3 gap-6">
            {[
              ["120+", "Projekte"],
              ["4,9★", "Bewertung"],
              ["3×", "mehr Anfragen"],
            ].map(([k, v], i) => (
              <Reveal key={v} delay={0.18 + i * 0.07}>
                <div>
                  <div className="font-display text-[clamp(24px,3vw,38px)] font-extrabold tracking-tight text-ink">
                    {k}
                  </div>
                  <div className="mt-1 font-mono text-[11px] uppercase tracking-[0.16em] text-muted">
                    {v}
                  </div>
                </div>
              </Reveal>
            ))}
          </div>
        </div>

        <div className="order-1 lg:order-2">
          <ParallaxImage
            src={IMG.owner}
            alt="Stolzer Betriebsinhaber in seiner Werkstatt"
            className="aspect-[4/5] w-full"
            amount={12}
          />
        </div>
      </div>
    </section>
  );
}
