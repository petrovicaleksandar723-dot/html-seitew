"use client";

import { Reveal } from "@/components/ui/reveal";
import { PLANS } from "@/lib/constants";

export function Pricing() {
  return (
    <section id="pakete" className="py-[clamp(90px,14vw,170px)]">
      <div className="lightfield left-1/2 top-1/3 h-[36vw] w-[36vw] -translate-x-1/2 bg-gold/[0.05]" />
      <div className="shell content relative z-10">
        <Reveal>
          <div className="mx-auto max-w-[680px] text-center">
            <span className="eyebrow justify-center">Pakete</span>
            <h2 className="mt-6 font-display text-[clamp(32px,5vw,56px)] font-bold leading-[1.04] tracking-[-0.02em]">
              Wähle, wie sichtbar dein Betrieb{" "}
              <span className="font-serif italic font-normal text-gradient-gold">
                werden soll.
              </span>
            </h2>
            <p className="mx-auto mt-6 max-w-[520px] font-body text-[16px] leading-relaxed text-dim">
              Drei klare Pakete — je nachdem, ob du starten, wachsen oder deinen
              Auftritt auf Premium-Niveau bringen willst.
            </p>
          </div>
        </Reveal>

        <div className="mt-16 grid items-stretch gap-5 lg:grid-cols-3">
          {PLANS.map((plan, i) => (
            <Reveal key={plan.name} delay={i * 0.07}>
              <div
                className={`relative flex h-full flex-col rounded-2xl p-8 ${
                  plan.featured
                    ? "glass border-gold/40 shadow-[0_30px_80px_-30px_rgba(216,178,116,0.5)]"
                    : "border border-line bg-white/[0.015]"
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
                  <span className="font-display text-[44px] font-extrabold tracking-[-0.03em]">
                    {plan.price}
                  </span>
                  <span className="font-body text-[14px] text-muted">
                    {plan.cadence}
                  </span>
                </div>
                <p className="mt-3 min-h-[60px] font-body text-[13.5px] leading-relaxed text-dim">
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
                      ? "bg-gradient-to-br from-gold-bright to-gold-deep text-[#1a1206] shadow-[0_14px_40px_-12px_rgba(216,178,116,0.7)]"
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
