"use client";

import { motion, useReducedMotion } from "framer-motion";
import {
  Reveal,
  AnimatedHeading,
  Eyebrow,
  Phone,
  LazyVideo,
  stagger,
  EASE,
} from "@/components/cl/ui";
import { SHOWREEL } from "@/lib/cl-data";

export function ClShowreel() {
  const reduce = useReducedMotion();

  return (
    <section className="relative px-0 py-16">
      {/* Header — kept inside the readable column */}
      <div className="mx-auto w-full max-w-[600px] px-5">
        <Eyebrow>Showreel</Eyebrow>
        <AnimatedHeading
          as="h2"
          className="mt-4 font-display text-[30px] font-extrabold leading-[1.08] tracking-tight"
          lines={["So sieht dein Content aus."]}
        />
        <Reveal delay={0.1}>
          <p className="mt-4 text-[15px] text-dim">
            Echte Beispiele aus unseren Reel-Produktionen – fertig für Instagram,
            TikTok &amp; Co.
          </p>
        </Reveal>
      </div>

      {/* Full-bleed horizontal scroll-snap row */}
      <div className="relative">
        <div className="no-bar mt-8 flex gap-4 overflow-x-auto px-5 pb-3 [scroll-snap-type:x_mandatory]">
          {SHOWREEL.map((item, i) => (
            <motion.div
              key={item.src}
              {...stagger(i)}
              className="flex-none [scroll-snap-align:center] text-center"
            >
              <motion.div
                whileHover={reduce ? undefined : { y: -6 }}
                transition={{ type: "spring", stiffness: 300, damping: 22 }}
                className="will-change-transform"
              >
                <Phone width={200} live={i === 0}>
                  <LazyVideo src={item.src} className="h-full w-full object-cover" />
                </Phone>
              </motion.div>
              <div className="mt-2.5 text-[12.5px] text-dim">{item.cap}</div>
            </motion.div>
          ))}
          {/* trailing spacer so the last card can center-snap and breathe */}
          <span aria-hidden className="block w-px flex-none" />
        </div>

        {/* Soft edge fade hinting more cards exist */}
        <div
          aria-hidden
          className="pointer-events-none absolute inset-y-0 right-0 w-16 bg-gradient-to-l from-bg to-transparent"
        />
      </div>

      {/* Quiet scroll-cue */}
      <motion.div
        initial={reduce ? false : { opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true, margin: "-10% 0px" }}
        transition={{ duration: 0.6, delay: 0.2, ease: EASE }}
        className="mx-auto mt-4 flex w-full max-w-[600px] items-center justify-center gap-2 px-5 font-mono text-[11px] font-bold uppercase tracking-[0.16em] text-muted"
      >
        <span>Wischen für mehr</span>
        <motion.span
          aria-hidden
          animate={reduce ? undefined : { x: [0, 5, 0] }}
          transition={{ duration: 1.8, repeat: Infinity, ease: EASE }}
          className="text-gold"
        >
          →
        </motion.span>
      </motion.div>
    </section>
  );
}
