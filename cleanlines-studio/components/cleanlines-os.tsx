"use client";

import dynamic from "next/dynamic";
import { useEffect, useRef, useState } from "react";
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
  // Default to desktop so SSR / first paint match; refine in the browser.
  // (Never read matchMedia during render — that would risk a hydration mismatch.)
  const [isDesktop, setIsDesktop] = useState(true);
  useEffect(() => {
    const mq = window.matchMedia("(min-width: 1024px)");
    const update = () => setIsDesktop(mq.matches);
    update();
    mq.addEventListener("change", update);
    return () => mq.removeEventListener("change", update);
  }, []);
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
      className="relative flex min-h-screen flex-col overflow-hidden bg-black py-[clamp(80px,12vw,140px)] lg:items-center lg:justify-center"
    >
      {/* 3D earth: a ~50vh top band on mobile, full-bleed stage on desktop */}
      <div className="relative z-0 h-[50vh] w-full lg:absolute lg:inset-0 lg:h-auto">
        <InView
          fallback={
            <div className="absolute inset-0 grid place-items-center">
              <div className="lightfield h-64 w-64 bg-gold/15" />
            </div>
          }
        >
          <OsCanvas
            progress={progress}
            velocity={velocity}
            offsetX={isDesktop ? 2.7 : 0}
          />
        </InView>
      </div>
      {/* fluid hand-off to neighbouring sections */}
      <div className="pointer-events-none absolute inset-x-0 top-0 z-[1] h-40 bg-gradient-to-b from-black to-transparent" />
      <div className="pointer-events-none absolute inset-x-0 bottom-0 z-[1] h-40 bg-gradient-to-t from-black to-transparent" />

      <div className="shell content relative z-10 mt-10 lg:mt-0">
        <div className="mx-auto max-w-[560px] text-center lg:mx-0 lg:text-left">
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
            <p className="mx-auto mt-6 max-w-[460px] font-body text-[16px] leading-relaxed text-dim lg:mx-0">
              Du bekommst nicht einfach ein paar Videos. Du bekommst ein klares
              Content-System, das deinen Betrieb regelmäßig sichtbar macht —
              Themen, Formate, Texte und Posting-Ideen mit Richtung.
            </p>
          </Reveal>

          <div className="mt-8 grid gap-3 text-left sm:grid-cols-2">
            {OS_MODULES.map((m, i) => (
              <motion.div
                key={m.title}
                initial={{ opacity: 0, y: 30, filter: "blur(6px)" }}
                whileInView={{ opacity: 1, y: 0, filter: "blur(0px)" }}
                whileHover={{ scale: 1.05, y: -6 }}
                viewport={{ once: true, margin: "-5% 0px" }}
                transition={{
                  duration: 0.6,
                  delay: i * 0.06,
                  ease: [0.22, 1, 0.36, 1],
                }}
                className="group cursor-pointer rounded-xl border border-line bg-bg/75 p-4 backdrop-blur-xl transition-colors duration-300 hover:border-gold/50 hover:shadow-[0_22px_60px_-22px_rgba(216,178,116,0.65)]"
                data-hot
              >
                <div className="flex items-center gap-2.5">
                  <span className="h-2 w-2 rounded-full bg-gold shadow-[0_0_12px_3px_rgba(216,178,116,0.85)]" />
                  <h3 className="font-display text-[17px] font-bold tracking-tight transition-colors group-hover:text-gold-bright">
                    {m.title}
                  </h3>
                </div>
                <p className="mt-1.5 font-body text-[13px] leading-relaxed text-dim transition-colors group-hover:text-ink">
                  {m.body}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
