"use client";

import { useState } from "react";
import { motion, AnimatePresence, useReducedMotion } from "framer-motion";
import { AnimatedHeading, EASE_OUT, ParallaxY } from "@/components/award/ux";
import { BRANCHES } from "@/lib/cl-data";

export function AwBranchen() {
  const [active, setActive] = useState(0);
  const reduce = useReducedMotion();
  const b = BRANCHES[active];

  return (
    <section id="branchen" className="py-24 md:py-32">
      <div className="mx-auto max-w-[1320px] px-5 sm:px-8">
        {/* Header */}
        <span className="font-mono text-[12px] uppercase tracking-[0.2em] text-gold">
          Branchen
        </span>
        <AnimatedHeading
          as="h2"
          lines={[
            <span key="a">
              Content, der zu deinem <span className="text-gold">Betrieb</span> passt.
            </span>,
          ]}
          className="mt-5 font-display text-[clamp(34px,5.5vw,68px)] font-extrabold leading-[1.02] tracking-[-0.03em] max-w-[14ch]"
        />

        {/* Preload all images (hidden) for instant switching */}
        <div aria-hidden className="pointer-events-none absolute h-0 w-0 overflow-hidden opacity-0">
          {BRANCHES.map((x, i) => (
            <img key={i} src={x.img} alt="" loading="lazy" />
          ))}
        </div>

        <div className="mt-14 grid gap-10 lg:grid-cols-[0.9fr_1.1fr] items-start">
          {/* LEFT — vertical tab list */}
          <ParallaxY amount={14}>
          <div role="tablist" aria-label="Branchen" className="flex flex-col">
            {BRANCHES.map((x, i) => {
              const isActive = i === active;
              return (
                <button
                  key={x.tab}
                  role="tab"
                  aria-selected={isActive}
                  onMouseEnter={() => setActive(i)}
                  onClick={() => setActive(i)}
                  className="group relative w-full cursor-pointer border-b border-line py-5 text-left"
                >
                  {isActive && (
                    <motion.span
                      layoutId="branacc"
                      className="absolute left-0 top-1/2 h-7 w-[3px] -translate-y-1/2 rounded bg-gradient-to-b from-gold to-gold-bright"
                      transition={{ type: "spring", stiffness: 320, damping: 30 }}
                    />
                  )}
                  <motion.span
                    animate={{ x: isActive ? 10 : 0 }}
                    transition={{ type: "spring", stiffness: 320, damping: 30 }}
                    className="flex items-baseline gap-4"
                  >
                    <span
                      className={`font-mono text-[13px] tracking-tight transition-colors duration-300 ${
                        isActive ? "text-gold" : "text-muted"
                      }`}
                    >
                      0{i + 1}
                    </span>
                    <span
                      className={`font-display text-[clamp(22px,2.4vw,34px)] font-bold tracking-tight transition-colors duration-300 ${
                        isActive ? "text-ink" : "text-muted group-hover:text-dim"
                      }`}
                    >
                      {x.tab}
                    </span>
                  </motion.span>
                </button>
              );
            })}
          </div>
          </ParallaxY>

          {/* RIGHT — visual + content panel */}
          <ParallaxY amount={38}>
          <div>
            {/* Visual */}
            <div className="relative aspect-[4/5] overflow-hidden rounded-[24px] border border-line bg-surface">
              <AnimatePresence mode="wait">
                <motion.img
                  key={active}
                  src={b.img}
                  alt=""
                  loading="lazy"
                  className="absolute inset-0 h-full w-full object-cover"
                  initial={
                    reduce
                      ? { opacity: 0 }
                      : { opacity: 0, scale: 1.06, filter: "blur(8px)" }
                  }
                  animate={
                    reduce
                      ? { opacity: 1 }
                      : { opacity: 1, scale: 1, filter: "blur(0px)" }
                  }
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.6, ease: EASE_OUT }}
                />
              </AnimatePresence>

              {/* Scrim */}
              <div className="absolute inset-0 bg-gradient-to-t from-bg via-bg/20 to-transparent" />

              {/* Metric badge */}
              <AnimatePresence mode="wait">
                <motion.div
                  key={active}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.35, ease: EASE_OUT }}
                  className="absolute bottom-5 left-5 rounded-full border border-white/20 bg-black/50 px-4 py-2 text-[14px] font-bold text-white backdrop-blur"
                >
                  {b.metric}
                </motion.div>
              </AnimatePresence>
            </div>

            {/* Content panel */}
            <div className="mt-6">
              <AnimatePresence mode="wait">
                <motion.div
                  key={active}
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  transition={{ duration: 0.35, ease: EASE_OUT }}
                >
                  <span className="font-mono text-[11px] font-bold uppercase tracking-[0.14em] text-gold">
                    Reel-Idee
                  </span>
                  <div className="mt-2 font-display text-[clamp(18px,1.6vw,24px)] font-bold leading-snug">
                    {b.reel}
                  </div>

                  <div className="mt-5">
                    <span className="font-mono text-[11px] font-bold uppercase tracking-[0.14em] text-gold">
                      Caption
                    </span>
                    <p className="mt-2 text-[15px] text-dim">{b.cap}</p>
                  </div>

                  <div className="mt-5">
                    <span className="font-mono text-[11px] font-bold uppercase tracking-[0.14em] text-gold">
                      Google-Beitrag
                    </span>
                    <p className="mt-2 text-[15px] text-dim">{b.google}</p>
                  </div>

                  <div className="mt-6 text-[16px] font-bold text-gold-bright">
                    <span className="text-gold">→ </span>
                    {b.cta}
                  </div>
                </motion.div>
              </AnimatePresence>
            </div>
          </div>
          </ParallaxY>
        </div>
      </div>
    </section>
  );
}
