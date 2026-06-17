"use client";

import { useRef } from "react";
import { motion, useReducedMotion, useScroll, useTransform } from "framer-motion";
import { Reveal } from "@/components/ui/reveal";
import { IMG } from "@/lib/content";

export function FinalCta() {
  const ref = useRef<HTMLDivElement>(null);
  const reduce = useReducedMotion();
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start end", "end start"],
  });
  const scale = useTransform(scrollYProgress, [0, 1], [1.08, 1]);
  const y = useTransform(scrollYProgress, [0, 1], ["-5%", "5%"]);

  return (
    <section
      id="kontakt"
      ref={ref}
      className="relative flex min-h-[88svh] items-center overflow-hidden"
    >
      <motion.div
        className="absolute inset-0"
        style={reduce ? undefined : { scale, y }}
      >
        <img
          src={IMG.skyline}
          alt="Skyline im goldenen Licht"
          className="h-full w-full object-cover"
        />
      </motion.div>
      <div className="absolute inset-0 bg-gradient-to-t from-bg via-bg/55 to-bg/30" />

      <div
        className="shell relative z-10 text-center"
        style={{ ["--max" as string]: "880px" }}
      >
        <Reveal>
          <span className="eyebrow justify-center">Bereit?</span>
        </Reveal>
        <Reveal delay={0.06}>
          <h2 className="mx-auto mt-6 max-w-[16ch] font-display text-[clamp(36px,7vw,88px)] font-extrabold leading-[0.98] tracking-[-0.03em]">
            Lass uns deinen Auftritt{" "}
            <span className="font-serif italic text-gold">premium machen.</span>
          </h2>
        </Reveal>
        <Reveal delay={0.14}>
          <p className="mx-auto mt-6 max-w-[480px] font-body text-[clamp(15px,1.6vw,18px)] leading-relaxed text-dim">
            Kostenloses Erstgespräch — wir zeigen dir konkret, wie dein Betrieb
            online wirken könnte.
          </p>
        </Reveal>
        <Reveal delay={0.2}>
          <div className="mt-9 flex flex-wrap justify-center gap-4">
            <a
              href="mailto:hallo@cleanlines.studio"
              className="rounded-full bg-gradient-to-br from-gold-bright to-gold-deep px-8 py-4 font-display text-[16px] font-bold text-[#1a1206] shadow-[0_18px_50px_-16px_rgba(216,178,116,0.7)] transition-transform duration-300 hover:scale-[1.03]"
            >
              Gespräch vereinbaren
            </a>
          </div>
        </Reveal>
      </div>
    </section>
  );
}
