"use client";

import dynamic from "next/dynamic";
import { Reveal } from "@/components/ui/reveal";
import { AnimatedHeading } from "@/components/ui/animated-heading";
import { OS_MODULES } from "@/lib/constants";

const OsCanvas = dynamic(() => import("@/components/scene/os-canvas"), {
  ssr: false,
  loading: () => (
    <div className="absolute inset-0 grid place-items-center">
      <div className="lightfield h-64 w-64 bg-gold/15" />
    </div>
  ),
});

export function CleanlinesOS() {
  return (
    <section id="system" className="py-[clamp(90px,14vw,170px)]">
      <div className="shell content relative z-10">
        <div className="max-w-[680px]">
          <Reveal>
            <span className="eyebrow">Cleanlines OS</span>
          </Reveal>
          <AnimatedHeading
            className="mt-6 font-display text-[clamp(32px,5vw,60px)] font-bold leading-[1.02] tracking-[-0.02em]"
            lines={[
              [{ t: "Ein System." }],
              [{ t: "Nicht nur einzelne Posts.", accent: true }],
            ]}
          />
          <Reveal delay={0.1}>
            <p className="mt-6 font-body text-[17px] leading-relaxed text-dim">
              Du bekommst nicht einfach ein paar Videos. Du bekommst ein klares
              Content-System, das deinen Betrieb regelmäßig sichtbar macht. Wir
              planen Themen, Formate, Texte und Posting-Ideen so, dass dein
              Auftritt nicht zufällig wirkt — sondern wie eine Marke mit
              Richtung.
            </p>
          </Reveal>
        </div>

        <div className="mt-16 grid items-center gap-12 lg:grid-cols-[0.9fr_1.1fr]">
          {/* WebGL core */}
          <div className="relative order-2 h-[420px] w-full lg:order-1 lg:h-[560px]">
            <OsCanvas />
            <div className="pointer-events-none absolute inset-0 grid place-items-center">
              <div className="text-center">
                <span className="font-mono text-[11px] uppercase tracking-[0.25em] text-gold/80">
                  Core
                </span>
                <div className="font-display text-2xl font-extrabold tracking-tight">
                  Cleanlines OS
                </div>
              </div>
            </div>
          </div>

          {/* Module cards */}
          <div className="order-1 grid gap-4 sm:grid-cols-2 lg:order-2">
            {OS_MODULES.map((m, i) => (
              <Reveal key={m.title} delay={i * 0.05}>
                <div className="glass h-full rounded-xl p-5 transition-transform duration-300 hover:-translate-y-1">
                  <div className="flex items-center gap-2">
                    <span className="h-1.5 w-1.5 rounded-full bg-gold shadow-[0_0_10px_2px_rgba(216,178,116,0.8)]" />
                    <h3 className="font-display text-[16px] font-bold tracking-tight">
                      {m.title}
                    </h3>
                  </div>
                  <p className="mt-2 font-body text-[13.5px] leading-relaxed text-dim">
                    {m.body}
                  </p>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
