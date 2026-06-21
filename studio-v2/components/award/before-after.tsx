"use client";

import { motion } from "framer-motion";

import { Reveal, AnimatedHeading, stagger, ParallaxY } from "@/components/award/ux";
import { Icon } from "@/components/cl/icons";
import { BEFORE, AFTER } from "@/lib/cl-data";

export function AwBeforeAfter() {
  return (
    <section className="py-24 md:py-32">
      <div className="mx-auto max-w-[1320px] px-5 sm:px-8">
        <ParallaxY amount={18}>
          <header className="max-w-[820px]">
            <span className="font-mono text-[12px] uppercase tracking-[0.2em] text-gold">
              Vorher / Nachher
            </span>
            <AnimatedHeading
              as="h2"
              lines={[
                <span key="a">Von „wir müssten mal posten“</span>,
                <span key="b">
                  zu einem klaren <span className="text-gold">System.</span>
                </span>,
              ]}
              className="mt-5 font-display text-[clamp(34px,5.5vw,64px)] font-extrabold leading-[1.04] tracking-[-0.03em]"
            />
          </header>
        </ParallaxY>

        <Reveal>
          <div className="relative mt-14 grid items-stretch gap-6 md:grid-cols-2">
            {/* Center connector (md+) */}
            <div className="pointer-events-none absolute left-1/2 top-1/2 z-10 hidden -translate-x-1/2 -translate-y-1/2 md:block">
              <div className="flex h-12 w-12 items-center justify-center rounded-full border border-line bg-bg-2 shadow-[0_18px_40px_-20px_rgba(0,0,0,0.6)]">
                <Icon name="arrow" className="h-5 w-5 text-gold" />
              </div>
            </div>

            {/* VORHER */}
            <ParallaxY amount={42} dir={1}>
            <div className="rounded-[24px] border border-line bg-gradient-to-b from-[#1a1418] to-[#120e11] p-8">
              <div className="flex items-baseline justify-between gap-4">
                <h3 className="font-display text-[14px] uppercase tracking-[0.12em] text-[#d98a8a]">
                  Vorher
                </h3>
                <span className="text-[12px] text-muted">Content als Last</span>
              </div>
              <ul className="mt-5">
                {BEFORE.map((item, i) => (
                  <motion.li
                    key={item}
                    {...stagger(i)}
                    className="relative flex items-start gap-3 py-2.5 text-[15px] text-[#cbc6bf]"
                  >
                    <span className="mt-0.5 font-extrabold text-[#d98a8a]">✕</span>
                    <span>{item}</span>
                  </motion.li>
                ))}
              </ul>
            </div>
            </ParallaxY>

            {/* NACHHER */}
            <ParallaxY amount={42} dir={-1}>
            <div className="rounded-[24px] border border-[rgba(120,190,140,0.28)] bg-gradient-to-b from-[#101a14] to-[#0b130e] p-8 shadow-[0_24px_60px_-30px_rgba(120,190,140,0.25)]">
              <div className="flex items-baseline justify-between gap-4">
                <h3 className="font-display text-[14px] uppercase tracking-[0.12em] text-[#7fcf9b]">
                  Nachher
                </h3>
                <span className="text-[12px] text-muted">Content als System</span>
              </div>
              <ul className="mt-5">
                {AFTER.map((item, i) => (
                  <motion.li
                    key={item}
                    {...stagger(i, 0.08)}
                    className="relative flex items-start gap-3 py-2.5 text-[15px] text-[#cbc6bf]"
                  >
                    <span className="mt-0.5 font-extrabold text-[#7fcf9b]">✓</span>
                    <span>{item}</span>
                  </motion.li>
                ))}
              </ul>
            </div>
            </ParallaxY>
          </div>
        </Reveal>
      </div>
    </section>
  );
}
