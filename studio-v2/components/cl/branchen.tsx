"use client";

import { useState } from "react";
import { motion, AnimatePresence, useReducedMotion } from "framer-motion";
import { AnimatedHeading, Eyebrow, Reveal, EASE } from "@/components/cl/ui";
import { Icon } from "@/components/cl/icons";
import { BRANCHES, MAIL } from "@/lib/cl-data";

export function ClBranchen() {
  const reduce = useReducedMotion();
  const [active, setActive] = useState(0);
  const b = BRANCHES[active];

  return (
    <section id="branchen" className="relative px-5 py-16">
      <div className="mx-auto w-full max-w-[600px]">
        <Eyebrow>Branchen</Eyebrow>

        <AnimatedHeading
          lines={[
            <>
              Content, der zu deinem <span className="text-gold">Betrieb</span> passt.
            </>,
          ]}
          className="mt-4 font-display text-[clamp(27px,8vw,40px)] font-extrabold leading-[1.12] tracking-[-0.02em]"
        />

        {/* Tabs */}
        <Reveal delay={0.05} blur={false}>
          <div
            className="no-bar mt-6 flex gap-2.5 overflow-x-auto pb-3"
            role="tablist"
            aria-label="Branchen"
          >
            {BRANCHES.map((branch, i) => {
              const on = i === active;
              return (
                <button
                  key={branch.tab}
                  type="button"
                  role="tab"
                  aria-selected={on}
                  onClick={() => setActive(i)}
                  className={`relative flex-none whitespace-nowrap rounded-full px-4 py-2.5 text-[14px] font-semibold transition-colors ${
                    on
                      ? "text-[#1a1206] font-bold"
                      : "border border-line bg-white/[0.03] text-dim"
                  }`}
                >
                  {on && (
                    <motion.span
                      layoutId="brancheTab"
                      className="absolute inset-0 -z-0 rounded-full bg-gradient-to-br from-gold to-gold-bright"
                      transition={{ type: "spring", stiffness: 380, damping: 32 }}
                    />
                  )}
                  <span className="relative z-10">{branch.tab}</span>
                </button>
              );
            })}
          </div>
        </Reveal>

        {/* Visual */}
        <Reveal delay={0.1}>
          <div className="relative mt-1.5 aspect-[16/11] overflow-hidden rounded-[20px] border border-line bg-surface">
            <AnimatePresence mode="wait">
              <motion.img
                key={active}
                src={b.img}
                alt=""
                loading="lazy"
                className="absolute inset-0 h-full w-full object-cover"
                initial={{ opacity: 0, scale: reduce ? 1 : 1.06 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.6, ease: EASE }}
              />
            </AnimatePresence>

            <div className="pointer-events-none absolute inset-0 bg-gradient-to-t from-bg via-bg/10 to-transparent" />

            <AnimatePresence mode="wait">
              <motion.div
                key={active}
                className="absolute bottom-3.5 left-3.5 rounded-full border border-white/20 bg-black/45 px-3.5 py-2 text-[13px] font-bold text-white"
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -6 }}
                transition={{ duration: 0.4, ease: EASE }}
              >
                {b.metric}
              </motion.div>
            </AnimatePresence>
          </div>
        </Reveal>

        {/* Content card */}
        <Reveal delay={0.14} blur={false}>
          <div className="mt-3.5 rounded-[18px] border border-line bg-gradient-to-b from-surface to-bg-2 p-5">
            <AnimatePresence mode="wait">
              <motion.div
                key={active}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.4, ease: EASE }}
              >
                <span className="font-mono text-[11px] font-extrabold uppercase tracking-[0.14em] text-gold">
                  Reel-Idee
                </span>
                <div className="mt-1.5 font-display text-[18px] font-bold leading-snug">
                  {b.reel}
                </div>

                <div className="mt-4">
                  <span className="font-mono text-[11px] font-extrabold uppercase tracking-[0.14em] text-gold">
                    Caption
                  </span>
                  <p className="mt-1.5 text-[14.5px] text-dim">{b.cap}</p>
                </div>

                <div className="mt-4">
                  <span className="font-mono text-[11px] font-extrabold uppercase tracking-[0.14em] text-gold">
                    Google-Beitrag
                  </span>
                  <p className="mt-1.5 text-[14.5px] text-dim">{b.google}</p>
                </div>

                <div className="mt-5 text-[15px] font-bold text-gold-bright">
                  <span className="text-gold">→ </span>
                  {b.cta}
                </div>
              </motion.div>
            </AnimatePresence>
          </div>
        </Reveal>

        {/* Preload all stills for instant switching */}
        <div aria-hidden className="pointer-events-none absolute h-0 w-0 overflow-hidden opacity-0">
          {BRANCHES.map((branch, i) =>
            i === active ? null : (
              <img key={branch.tab} src={branch.img} alt="" loading="lazy" />
            )
          )}
        </div>
      </div>
    </section>
  );
}
