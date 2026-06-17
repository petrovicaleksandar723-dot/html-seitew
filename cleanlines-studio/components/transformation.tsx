"use client";

import { Reveal } from "@/components/ui/reveal";
import { AnimatedHeading } from "@/components/ui/animated-heading";
import { MediaBackdrop } from "@/components/ui/media-backdrop";
import { TRANSFORM_BEFORE, TRANSFORM_AFTER } from "@/lib/constants";
import { asset } from "@/lib/asset";

const BG = [asset("/videos/example-3.mp4"), asset("/videos/ambient-2.mp4")];

export function Transformation() {
  return (
    <section className="py-[clamp(90px,14vw,170px)]">
      <MediaBackdrop videos={BG} opacity={0.2} />
      <div className="shell content relative z-10">
        <div className="max-w-[680px]">
          <Reveal>
            <span className="eyebrow">Transformation</span>
          </Reveal>
          <AnimatedHeading
            className="mt-6 font-display text-[clamp(32px,5vw,60px)] font-bold leading-[1.02] tracking-[-0.02em]"
            lines={[
              [{ t: "Aus zufälligen Posts wird ein" }],
              [{ t: "klarer Markenauftritt.", accent: true }],
            ]}
          />
        </div>

        <div className="mt-14 grid gap-5 md:grid-cols-2">
          <Reveal delay={0.05}>
            <div className="relative h-full rounded-2xl border border-line bg-bg/40 p-8 backdrop-blur-md">
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
