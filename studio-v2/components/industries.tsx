"use client";

import { Reveal } from "@/components/ui/reveal";
import { ParallaxImage } from "@/components/ui/parallax-image";
import { INDUSTRIES } from "@/lib/content";

export function Industries() {
  return (
    <section id="branchen" className="relative py-[clamp(70px,12vw,150px)]">
      <div className="shell" style={{ ["--max" as string]: "1280px" }}>
        <div className="flex flex-wrap items-end justify-between gap-6">
          <div className="max-w-[640px]">
            <Reveal>
              <span className="eyebrow">Branchen</span>
            </Reveal>
            <Reveal delay={0.05}>
              <h2 className="mt-6 font-display text-[clamp(30px,5vw,64px)] font-bold leading-[1.02] tracking-[-0.02em]">
                Content, der zu deinem{" "}
                <span className="font-serif italic text-gold">Betrieb passt.</span>
              </h2>
            </Reveal>
          </div>
          <Reveal delay={0.1}>
            <p className="max-w-[340px] font-body text-[15px] leading-relaxed text-dim">
              Jede Branche verkauft anders — Tonalität, Formate und Bildwelt
              passen wir genau an.
            </p>
          </Reveal>
        </div>

        <div className="mt-14 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {INDUSTRIES.map((ind, i) => (
            <Reveal key={ind.title} delay={i * 0.08}>
              <div className="group relative overflow-hidden rounded-[18px]">
                <ParallaxImage
                  src={ind.image}
                  alt={ind.title}
                  rounded={false}
                  className="aspect-[4/5] w-full"
                  amount={8}
                />
                <div className="pointer-events-none absolute inset-0 bg-gradient-to-t from-bg via-bg/10 to-transparent" />
                <div className="absolute inset-x-0 bottom-0 p-6">
                  <h3 className="font-display text-[24px] font-bold tracking-tight">
                    {ind.title}
                  </h3>
                  <p className="mt-1.5 max-w-[90%] font-body text-[14px] leading-snug text-dim">
                    {ind.body}
                  </p>
                </div>
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}
