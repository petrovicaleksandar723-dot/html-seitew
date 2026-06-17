"use client";

import dynamic from "next/dynamic";
import { useRef } from "react";
import {
  motion,
  useScroll,
  useMotionValueEvent,
  useVelocity,
  useSpring,
} from "framer-motion";
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
  const section = useRef<HTMLDivElement>(null);
  const progress = useRef(0);
  const velocity = useRef(0);
  const { scrollYProgress } = useScroll({
    target: section,
    offset: ["start end", "end start"],
  });
  const rawVel = useVelocity(scrollYProgress);
  const smoothVel = useSpring(rawVel, { damping: 50, stiffness: 300 });
  useMotionValueEvent(scrollYProgress, "change", (v) => {
    progress.current = v;
  });
  useMotionValueEvent(smoothVel, "change", (v) => {
    velocity.current = v;
  });

  return (
    <section
      id="system"
      ref={section}
      className="relative flex min-h-screen items-center overflow-hidden py-[clamp(80px,12vw,140px)]"
    >
      {/* 3D earth fills the stage */}
      <div className="absolute inset-0 z-0">
        <OsCanvas progress={progress} velocity={velocity} />
      </div>
      <div className="pointer-events-none absolute inset-0 z-[1] bg-[radial-gradient(130%_130%_at_50%_50%,transparent_55%,rgba(5,5,5,0.72)_100%)]" />

      <div className="shell content relative z-10 grid w-full items-center gap-10 lg:grid-cols-[1fr_1fr]">
          <div>
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
              <p className="mt-6 max-w-[460px] font-body text-[16px] leading-relaxed text-dim">
                Du bekommst nicht einfach ein paar Videos. Du bekommst ein
                klares Content-System, das deinen Betrieb regelmäßig sichtbar
                macht — Themen, Formate, Texte und Posting-Ideen mit Richtung.
              </p>
            </Reveal>
            <div className="mt-6 font-mono text-[11px] uppercase tracking-[0.25em] text-gold/70">
              Core · Cleanlines OS
            </div>
          </div>

          {/* module cards float in on the right */}
          <div className="grid gap-3 sm:grid-cols-2">
            {OS_MODULES.map((m, i) => (
              <motion.div
                key={m.title}
                initial={{ opacity: 0, y: 30, filter: "blur(6px)" }}
                whileInView={{ opacity: 1, y: 0, filter: "blur(0px)" }}
                viewport={{ once: true, margin: "-5% 0px" }}
                transition={{
                  duration: 0.7,
                  delay: i * 0.08,
                  ease: [0.22, 1, 0.36, 1],
                }}
                className="rounded-xl border border-line bg-bg/75 p-4 backdrop-blur-xl transition-transform duration-300 hover:-translate-y-1"
              >
                <div className="flex items-center gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-gold shadow-[0_0_10px_2px_rgba(216,178,116,0.8)]" />
                  <h3 className="font-display text-[15px] font-bold tracking-tight">
                    {m.title}
                  </h3>
                </div>
                <p className="mt-1.5 font-body text-[12.5px] leading-relaxed text-dim">
                  {m.body}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
    </section>
  );
}
