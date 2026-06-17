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
import { InView } from "@/components/ui/in-view";
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
      className="relative flex min-h-screen items-center overflow-hidden bg-black py-[clamp(80px,12vw,140px)]"
    >
      {/* 3D earth fills the stage */}
      <div className="absolute inset-0 z-0">
        <InView
          fallback={
            <div className="absolute inset-0 grid place-items-center">
              <div className="lightfield h-64 w-64 bg-gold/15" />
            </div>
          }
        >
          <OsCanvas progress={progress} velocity={velocity} />
        </InView>
      </div>
      {/* only a soft left wash so the copy stays readable — earth floats free */}
      <div className="pointer-events-none absolute inset-y-0 left-0 z-[1] w-[55%] bg-gradient-to-r from-black via-black/50 to-transparent" />
      {/* fluid hand-off to neighbouring sections */}
      <div className="pointer-events-none absolute inset-x-0 top-0 z-[1] h-40 bg-gradient-to-b from-black to-transparent" />
      <div className="pointer-events-none absolute inset-x-0 bottom-0 z-[1] h-40 bg-gradient-to-t from-black to-transparent" />

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
                whileHover={{ scale: 1.06, y: -8 }}
                viewport={{ once: true, margin: "-5% 0px" }}
                transition={{
                  duration: 0.6,
                  delay: i * 0.08,
                  ease: [0.22, 1, 0.36, 1],
                }}
                className="group cursor-pointer rounded-xl border border-line bg-bg/75 p-5 backdrop-blur-xl transition-colors duration-300 hover:border-gold/50 hover:shadow-[0_22px_60px_-22px_rgba(216,178,116,0.65)]"
                data-hot
              >
                <div className="flex items-center gap-2.5">
                  <span className="h-2 w-2 rounded-full bg-gold shadow-[0_0_12px_3px_rgba(216,178,116,0.85)]" />
                  <h3 className="font-display text-[19px] font-bold tracking-tight transition-colors group-hover:text-gold-bright">
                    {m.title}
                  </h3>
                </div>
                <p className="mt-2 font-body text-[14px] leading-relaxed text-dim transition-colors group-hover:text-ink">
                  {m.body}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
    </section>
  );
}
