"use client";

import { useEffect, useRef, useState } from "react";
import {
  motion,
  useReducedMotion,
  useScroll,
  useTransform,
  useSpring,
} from "framer-motion";
import { Reveal } from "@/components/ui/reveal";
import { AnimatedHeading } from "@/components/ui/animated-heading";
import { PIPELINE } from "@/lib/constants";

function StepCard({ n, title, body }: { n: string; title: string; body: string }) {
  return (
    <div className="relative w-[82vw] flex-none sm:w-[420px]">
      <div className="flex items-center gap-4">
        <span className="font-display text-[clamp(48px,7vw,84px)] font-extrabold leading-none text-transparent [-webkit-text-stroke:1px_rgba(216,178,116,0.55)]">
          {n}
        </span>
        <span className="h-3.5 w-3.5 rounded-full border-2 border-gold bg-bg shadow-[0_0_16px_3px_rgba(216,178,116,0.6)]" />
        <span className="h-px flex-1 bg-gradient-to-r from-gold/40 to-transparent" />
      </div>
      <div className="glass mt-6 rounded-2xl p-7">
        <h3 className="font-display text-[24px] font-bold tracking-tight">{title}</h3>
        <p className="mt-3 font-body text-[15px] leading-relaxed text-dim">{body}</p>
      </div>
    </div>
  );
}

function PinnedTimeline() {
  const reduce = useReducedMotion();
  const section = useRef<HTMLDivElement>(null);
  const track = useRef<HTMLDivElement>(null);
  const [distance, setDistance] = useState(0);

  useEffect(() => {
    const measure = () => {
      if (!track.current) return;
      setDistance(Math.max(0, track.current.scrollWidth - window.innerWidth + 80));
    };
    measure();
    window.addEventListener("resize", measure);
    return () => window.removeEventListener("resize", measure);
  }, []);

  const { scrollYProgress } = useScroll({
    target: section,
    offset: ["start start", "end end"],
  });
  const xRaw = useTransform(scrollYProgress, [0, 1], [0, -distance]);
  const x = useSpring(xRaw, { stiffness: 120, damping: 30, mass: 0.5 });
  const lineScale = useTransform(scrollYProgress, [0.05, 0.95], [0, 1]);

  if (reduce) {
    return (
      <div className="shell content no-bar mt-12 flex gap-8 overflow-x-auto pb-4">
        {PIPELINE.map((s) => (
          <StepCard key={s.n} {...s} />
        ))}
      </div>
    );
  }

  return (
    <div
      ref={section}
      style={{ height: `${Math.max(distance, 1) + 900}px` }}
      className="relative mt-6"
    >
      <div className="sticky top-0 flex h-screen flex-col justify-center overflow-hidden">
        {/* global scrub progress line */}
        <div className="shell mb-12">
          <div className="h-px w-full bg-line">
            <motion.div
              style={{ scaleX: lineScale }}
              className="h-full origin-left bg-gradient-to-r from-gold-bright via-gold to-gold-deep"
            />
          </div>
        </div>
        <motion.div
          ref={track}
          style={{ x }}
          className="flex gap-8 pl-[max(24px,calc((100vw-1240px)/2))] pr-24"
        >
          {PIPELINE.map((s) => (
            <StepCard key={s.n} {...s} />
          ))}
        </motion.div>
      </div>
    </div>
  );
}

export function Pipeline() {
  return (
    <section id="pipeline" className="py-[clamp(90px,14vw,170px)]">
      <div className="shell content relative z-10">
        <Reveal>
          <span className="eyebrow">Pipeline</span>
        </Reveal>
        <AnimatedHeading
          className="mt-6 max-w-[760px] font-display text-[clamp(32px,5vw,60px)] font-bold leading-[1.02] tracking-[-0.02em]"
          lines={[
            [{ t: "Von der Analyse zum" }],
            [{ t: "laufenden Content-System.", accent: true }],
          ]}
        />
        <Reveal delay={0.1}>
          <p className="mt-6 max-w-[640px] font-body text-[17px] leading-relaxed text-dim">
            Vom ersten Blick auf deinen Betrieb bis zum fertigen Content läuft
            alles klar, schnell und ohne komplizierte Agenturprozesse.
          </p>
        </Reveal>
      </div>

      <PinnedTimeline />
    </section>
  );
}
