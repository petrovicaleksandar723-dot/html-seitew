"use client";

import { Reveal } from "@/components/ui/reveal";
import { SERVICES } from "@/lib/constants";

export function Services() {
  return (
    <section className="py-[clamp(90px,14vw,170px)]">
      <div className="shell content relative z-10">
        <Reveal>
          <div className="max-w-[640px]">
            <span className="eyebrow">Mehr als Content</span>
            <h2 className="mt-6 font-display text-[clamp(32px,5vw,60px)] font-bold leading-[1.02] tracking-[-0.02em]">
              Mehr als nur{" "}
              <span className="font-serif italic font-normal text-gold">
                Content.
              </span>
            </h2>
            <p className="mt-6 font-body text-[17px] leading-relaxed text-dim">
              Ein starker Auftritt besteht nicht nur aus Reels. Website,
              Branding, Google, Bewertungen und Social Media müssen
              zusammenpassen, damit Kunden schneller Vertrauen aufbauen.
            </p>
          </div>
        </Reveal>

        <div className="mt-14 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {SERVICES.map((s, i) => (
            <Reveal key={s.title} delay={i * 0.05}>
              <div className="group flex h-full flex-col justify-between rounded-2xl border border-line bg-white/[0.015] p-7 transition-[border-color,transform] duration-300 hover:-translate-y-1 hover:border-gold/30">
                <div>
                  <h3 className="font-display text-[20px] font-bold tracking-tight">
                    {s.title}
                  </h3>
                  <p className="mt-3 font-body text-[14px] leading-relaxed text-dim">
                    {s.body}
                  </p>
                </div>
                <div className="mt-8 flex items-center justify-between border-t border-line pt-5">
                  <span className="font-display text-[17px] font-bold text-gold">
                    {s.price}
                  </span>
                  <span className="font-mono text-[11px] uppercase tracking-[0.15em] text-muted transition-colors group-hover:text-ink">
                    Mehr erfahren →
                  </span>
                </div>
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}
