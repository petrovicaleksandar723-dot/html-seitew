"use client";

import { useState } from "react";
import { Reveal } from "@/components/ui/reveal";
import { INDUSTRIES } from "@/lib/constants";

export function Industries() {
  const [active, setActive] = useState(0);

  return (
    <section id="branchen" className="py-[clamp(90px,14vw,170px)]">
      <div className="shell content relative z-10">
        <Reveal>
          <div className="max-w-[640px]">
            <span className="eyebrow">Branchen</span>
            <h2 className="mt-6 font-display text-[clamp(32px,5vw,60px)] font-bold leading-[1.02] tracking-[-0.02em]">
              Content, der zu deinem{" "}
              <span className="font-serif italic font-normal text-gold">
                Betrieb passt.
              </span>
            </h2>
            <p className="mt-6 font-body text-[17px] leading-relaxed text-dim">
              Jede Branche verkauft anders. Ein Restaurant verkauft Atmosphäre.
              Ein Friseur verkauft Stil. Ein Handwerker verkauft Vertrauen. Ein
              Kosmetikstudio verkauft Ergebnis und Gefühl. Wir erstellen
              Inhalte, die zu deinem Betrieb, deinen Kunden und deinem Angebot
              passen — nicht irgendeinen Standard-Content.
            </p>
          </div>
        </Reveal>

        <div className="mt-14 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {INDUSTRIES.map((ind, i) => (
            <Reveal key={ind.title} delay={i * 0.05}>
              <button
                onMouseEnter={() => setActive(i)}
                onFocus={() => setActive(i)}
                className="group relative h-full w-full overflow-hidden rounded-2xl border border-line bg-white/[0.015] p-7 text-left transition-[border-color,transform] duration-300 hover:-translate-y-1 hover:border-white/25"
                style={{
                  boxShadow:
                    active === i
                      ? `0 24px 60px -28px ${ind.accent}66, inset 0 0 0 1px ${ind.accent}55`
                      : undefined,
                }}
              >
                <div
                  className="lightfield -right-10 -top-10 h-40 w-40 opacity-0 transition-opacity duration-500 group-hover:opacity-100"
                  style={{ background: `${ind.accent}22` }}
                />
                <div className="relative">
                  <span
                    className="font-mono text-[12px] tracking-[0.18em]"
                    style={{ color: ind.accent }}
                  >
                    {String(i + 1).padStart(2, "0")}
                  </span>
                  <h3 className="mt-3 font-display text-[22px] font-bold tracking-tight">
                    {ind.title}
                  </h3>
                  <p className="mt-2 font-body text-[14px] leading-relaxed text-dim">
                    {ind.body}
                  </p>
                </div>
              </button>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}
