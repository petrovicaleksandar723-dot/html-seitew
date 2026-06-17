"use client";

import { Reveal } from "@/components/ui/reveal";
import { TRANSFORM_BEFORE, TRANSFORM_AFTER } from "@/lib/constants";

export function Transformation() {
  return (
    <section className="py-[clamp(90px,14vw,170px)]">
      <div className="shell content relative z-10">
        <Reveal>
          <div className="max-w-[640px]">
            <span className="eyebrow">Transformation</span>
            <h2 className="mt-6 font-display text-[clamp(32px,5vw,60px)] font-bold leading-[1.02] tracking-[-0.02em]">
              Aus zufälligen Posts wird ein{" "}
              <span className="font-serif italic font-normal text-gradient-gold">
                klarer Markenauftritt.
              </span>
            </h2>
          </div>
        </Reveal>

        <div className="mt-14 grid gap-5 md:grid-cols-2">
          <Reveal delay={0.05}>
            <div className="relative h-full rounded-2xl border border-line bg-white/[0.015] p-8">
              <span className="font-mono text-[11px] uppercase tracking-[0.2em] text-muted">
                Vorher
              </span>
              <ul className="mt-6 space-y-4">
                {TRANSFORM_BEFORE.map((t) => (
                  <li
                    key={t}
                    className="flex items-start gap-3 font-body text-[15.5px] text-dim/80"
                  >
                    <span className="mt-0.5 text-[15px] text-muted">✕</span>
                    {t}
                  </li>
                ))}
              </ul>
            </div>
          </Reveal>

          <Reveal delay={0.12}>
            <div className="glass relative h-full overflow-hidden rounded-2xl p-8">
              <div className="lightfield -right-10 -top-10 h-56 w-56 bg-gold/15" />
              <span className="relative font-mono text-[11px] uppercase tracking-[0.2em] text-gold">
                Nachher
              </span>
              <ul className="relative mt-6 space-y-4">
                {TRANSFORM_AFTER.map((t) => (
                  <li
                    key={t}
                    className="flex items-start gap-3 font-body text-[15.5px] text-ink"
                  >
                    <span className="mt-0.5 text-gold">✓</span>
                    {t}
                  </li>
                ))}
              </ul>
            </div>
          </Reveal>
        </div>
      </div>
    </section>
  );
}
