"use client";

import { Reveal } from "@/components/ui/reveal";
import { PLANS } from "@/lib/content";

export function Pricing() {
  return (
    <section id="pakete" className="relative py-[clamp(70px,12vw,150px)]">
      <div className="shell" style={{ ["--max" as string]: "1280px" }}>
        <div className="mx-auto max-w-[680px] text-center">
          <Reveal>
            <span className="eyebrow justify-center">Pakete</span>
          </Reveal>
          <Reveal delay={0.05}>
            <h2 className="mt-6 font-display text-[clamp(30px,5vw,60px)] font-bold leading-[1.04] tracking-[-0.02em]">
              Wähle, wie sichtbar dein Betrieb{" "}
              <span className="font-serif italic text-gold">werden soll.</span>
            </h2>
          </Reveal>
        </div>

        <div className="mt-16 grid items-stretch gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {PLANS.map((plan, i) => (
            <Reveal key={plan.name} delay={i * 0.08} className="h-full">
              <div
                className={`relative flex h-full flex-col rounded-[20px] p-8 ${
                  plan.featured
                    ? "border border-gold/40 bg-surface shadow-[0_30px_80px_-30px_rgba(216,178,116,0.5)]"
                    : "border border-line bg-bg/40"
                }`}
              >
                {plan.featured && (
                  <span className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-gradient-to-br from-gold-bright to-gold-deep px-4 py-1 font-mono text-[10px] uppercase tracking-[0.15em] text-[#1a1206]">
                    Beliebt
                  </span>
                )}
                <div className="font-mono text-[12px] uppercase tracking-[0.18em] text-muted">
                  {plan.name}
                </div>
                <div className="mt-4 flex items-baseline gap-1">
                  <span className="font-display text-[clamp(34px,4vw,46px)] font-extrabold tracking-[-0.03em]">
                    {plan.price}
                  </span>
                  <span className="font-body text-[14px] text-muted">
                    {plan.cadence}
                  </span>
                </div>
                <p className="mt-3 min-h-[48px] font-body text-[13.5px] leading-relaxed text-dim">
                  {plan.blurb}
                </p>
                <ul className="mt-6 flex-1 space-y-3 border-t border-line pt-6">
                  {plan.features.map((f) => (
                    <li
                      key={f}
                      className="flex items-start gap-3 font-body text-[13.5px] text-dim"
                    >
                      <span className="mt-0.5 text-gold">✓</span>
                      {f}
                    </li>
                  ))}
                </ul>
                <a
                  href="#kontakt"
                  className={`mt-8 inline-flex w-full items-center justify-center rounded-full px-6 py-3.5 font-display text-[14px] font-bold transition-transform duration-300 hover:scale-[1.02] ${
                    plan.featured
                      ? "bg-gradient-to-br from-gold-bright to-gold-deep text-[#1a1206]"
                      : "border border-white/20 text-ink hover:border-white/40"
                  }`}
                >
                  {plan.cta}
                </a>
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}
