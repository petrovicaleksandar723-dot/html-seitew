"use client";

import { motion } from "framer-motion";
import { Reveal, AnimatedHeading, Eyebrow, stagger } from "@/components/cl/ui";
import { BEFORE, AFTER } from "@/lib/cl-data";

export function ClBeforeAfter() {
  return (
    <section className="relative px-5 py-16">
      <div className="mx-auto w-full max-w-[600px]">
        <Eyebrow>Vorher / Nachher</Eyebrow>

        <AnimatedHeading
          as="h2"
          delay={0}
          className="mt-4 font-display text-[clamp(25px,7.5vw,38px)] font-extrabold leading-[1.1] tracking-[-0.02em] text-ink"
          lines={[
            <>Von „wir müssten mal posten“</>,
            <>
              zu einem klaren <span className="text-gold">System.</span>
            </>,
          ]}
        />

        <div className="mt-6 flex flex-col gap-3.5">
          <Reveal delay={0.05}>
            <div className="rounded-[18px] border border-line bg-gradient-to-b from-[#1a1418] to-[#120e11] p-5">
              <h4 className="mb-3.5 font-display text-[14px] uppercase tracking-[0.1em] text-[#d98a8a]">
                Vorher
              </h4>
              <ul>
                {BEFORE.map((item, i) => (
                  <motion.li
                    key={item}
                    {...stagger(i)}
                    className="relative flex pl-7 text-[14.5px] text-[#d7d3cc]"
                  >
                    <span className="absolute left-0 font-extrabold text-[#d98a8a]">
                      ✕
                    </span>
                    {item}
                  </motion.li>
                ))}
              </ul>
            </div>
          </Reveal>

          <Reveal delay={0.15}>
            <div className="rounded-[18px] border border-[rgba(120,190,140,0.25)] bg-gradient-to-b from-[#101a14] to-[#0b130e] p-5">
              <h4 className="mb-3.5 font-display text-[14px] uppercase tracking-[0.1em] text-[#7fcf9b]">
                Nachher
              </h4>
              <ul>
                {AFTER.map((item, i) => (
                  <motion.li
                    key={item}
                    {...stagger(i, 0.12)}
                    className="relative flex pl-7 text-[14.5px] text-[#d7d3cc]"
                  >
                    <span className="absolute left-0 font-extrabold text-[#7fcf9b]">
                      ✓
                    </span>
                    {item}
                  </motion.li>
                ))}
              </ul>
            </div>
          </Reveal>
        </div>
      </div>
    </section>
  );
}
