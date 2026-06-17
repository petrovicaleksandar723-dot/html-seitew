"use client";

import { Reveal } from "@/components/ui/reveal";
import { AnimatedHeading } from "@/components/ui/animated-heading";
import { MediaBackdrop } from "@/components/ui/media-backdrop";
import { SERVICES } from "@/lib/constants";
import { asset } from "@/lib/asset";

const BG = [
  asset("/videos/example-1.mp4"),
  asset("/videos/reel-2.mp4"),
  asset("/videos/example-3.mp4"),
  asset("/videos/reel-1.mp4"),
];

export function Services() {
  return (
    <section className="py-[clamp(90px,14vw,170px)]">
      <MediaBackdrop videos={BG} opacity={0.1} />
      <div className="shell content relative z-10">
        <div className="max-w-[680px]">
          <Reveal>
            <span className="eyebrow">Mehr als Content</span>
          </Reveal>
          <AnimatedHeading
            className="mt-6 font-display text-[clamp(32px,5vw,60px)] font-bold leading-[1.02] tracking-[-0.02em]"
            lines={[[{ t: "Mehr als nur" }, { t: "Content.", accent: true }]]}
          />
          <Reveal delay={0.1}>
            <p className="mt-6 font-body text-[17px] leading-relaxed text-dim">
              Ein starker Auftritt besteht nicht nur aus Reels. Website,
              Branding, Google, Bewertungen und Social Media müssen
              zusammenpassen, damit Kunden schneller Vertrauen aufbauen.
            </p>
          </Reveal>
        </div>

        <div className="mt-14 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {SERVICES.map((s, i) => (
            <Reveal key={s.title} delay={i * 0.05}>
              <div className="group flex h-full flex-col justify-between rounded-2xl border border-line bg-bg/40 p-7 backdrop-blur-md transition-[border-color,transform] duration-300 hover:-translate-y-1 hover:border-gold/30">
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
