"use client";

import { Reveal } from "@/components/ui/reveal";
import { ParallaxImage } from "@/components/ui/parallax-image";
import { SERVICES } from "@/lib/content";

export function Services() {
  return (
    <section id="leistungen" className="relative py-[clamp(70px,12vw,150px)]">
      <div className="shell" style={{ ["--max" as string]: "1280px" }}>
        <div className="max-w-[760px]">
          <Reveal>
            <span className="eyebrow">Leistungen</span>
          </Reveal>
          <Reveal delay={0.05}>
            <h2 className="mt-6 font-display text-[clamp(30px,5vw,64px)] font-bold leading-[1.02] tracking-[-0.02em]">
              Alles, was deinen Betrieb{" "}
              <span className="font-serif italic text-gold">sichtbar macht.</span>
            </h2>
          </Reveal>
        </div>

        <div className="mt-16 space-y-[clamp(48px,8vw,110px)]">
          {SERVICES.map((s, i) => (
            <div
              key={s.n}
              className={`grid items-center gap-10 lg:grid-cols-2 lg:gap-16 ${
                i % 2 === 1 ? "lg:[&>*:first-child]:order-2" : ""
              }`}
            >
              <ParallaxImage
                src={s.image}
                alt={s.title}
                className="aspect-[16/11] w-full"
              />
              <div>
                <Reveal>
                  <span className="font-display text-[clamp(40px,6vw,72px)] font-extrabold leading-none text-transparent [-webkit-text-stroke:1px_rgba(216,178,116,0.5)]">
                    {s.n}
                  </span>
                </Reveal>
                <Reveal delay={0.06}>
                  <h3 className="mt-5 font-display text-[clamp(24px,3vw,40px)] font-bold tracking-tight">
                    {s.title}
                  </h3>
                </Reveal>
                <Reveal delay={0.12}>
                  <p className="mt-4 max-w-[460px] font-body text-[clamp(15px,1.5vw,17.5px)] leading-relaxed text-dim">
                    {s.body}
                  </p>
                </Reveal>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
