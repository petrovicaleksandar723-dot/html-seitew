"use client";

import { Reveal } from "@/components/ui/reveal";
import { STEPS } from "@/lib/content";

export function Process() {
  return (
    <section id="prozess" className="relative py-[clamp(70px,12vw,150px)]">
      <div className="shell" style={{ ["--max" as string]: "1280px" }}>
        <div className="max-w-[760px]">
          <Reveal>
            <span className="eyebrow">Prozess</span>
          </Reveal>
          <Reveal delay={0.05}>
            <h2 className="mt-6 font-display text-[clamp(30px,5vw,64px)] font-bold leading-[1.02] tracking-[-0.02em]">
              Von der Analyse zum{" "}
              <span className="font-serif italic text-gold">
                laufenden Content-System.
              </span>
            </h2>
          </Reveal>
        </div>

        <div className="mt-16 grid gap-px overflow-hidden rounded-[18px] border border-line bg-line sm:grid-cols-2 lg:grid-cols-4">
          {STEPS.map((s, i) => (
            <Reveal key={s.n} delay={i * 0.08}>
              <div className="group h-full bg-bg p-7 transition-colors duration-500 hover:bg-surface">
                <div className="flex items-center gap-3">
                  <span className="font-mono text-[12px] text-gold">{s.n}</span>
                  <span className="h-px flex-1 bg-gradient-to-r from-gold/40 to-transparent" />
                </div>
                <h3 className="mt-7 font-display text-[22px] font-bold tracking-tight">
                  {s.title}
                </h3>
                <p className="mt-3 font-body text-[14.5px] leading-relaxed text-dim">
                  {s.body}
                </p>
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}
