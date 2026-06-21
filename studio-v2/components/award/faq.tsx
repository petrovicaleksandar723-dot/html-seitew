"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

import { Reveal, AnimatedHeading, EASE_OUT } from "@/components/award/ux";
import { Icon } from "@/components/cl/icons";
import { FAQ, MAIL } from "@/lib/cl-data";

export function AwFaq() {
  const [open, setOpen] = useState(0);

  return (
    <section id="faq" className="py-24 md:py-32">
      <div className="mx-auto max-w-[1320px] px-5 sm:px-8">
        <div className="grid items-start gap-10 lg:grid-cols-[0.8fr_1.2fr]">
          {/* LEFT — sticky heading */}
          <div className="self-start lg:sticky lg:top-28">
            <span className="font-mono text-[12px] uppercase tracking-[0.2em] text-gold">
              FAQ
            </span>
            <AnimatedHeading
              as="h2"
              lines={[
                <span key="a">
                  Häufige <span className="text-gold">Fragen.</span>
                </span>,
              ]}
              className="mt-4 font-display text-[clamp(30px,4vw,56px)] font-extrabold tracking-[-0.03em]"
            />
            <Reveal delay={0.1}>
              <p className="mt-5 max-w-[320px] text-[15px] text-dim">
                Noch offene Fragen? Schreib uns direkt — wir antworten innerhalb von
                24 Stunden.
              </p>
            </Reveal>
            <a
              href={`mailto:${MAIL}`}
              className="mt-5 inline-flex cursor-pointer items-center gap-2 text-[15px] font-semibold text-gold-bright"
            >
              {MAIL} <Icon name="arrow" className="h-4 w-4" />
            </a>
          </div>

          {/* RIGHT — accordion */}
          <div className="flex flex-col gap-3">
            {FAQ.map(({ q, a }, i) => {
              const isOpen = open === i;
              return (
                <div
                  key={q}
                  className={`overflow-hidden rounded-[18px] border bg-gradient-to-b from-surface to-bg-2 transition-colors duration-300 ${
                    isOpen ? "border-gold/40" : "border-line"
                  }`}
                >
                  <button
                    onClick={() => setOpen(isOpen ? -1 : i)}
                    className="flex w-full cursor-pointer items-center justify-between gap-5 px-6 py-5 text-left"
                  >
                    <span className="font-display text-[clamp(16px,1.3vw,19px)] font-bold">
                      {q}
                    </span>
                    <span className="relative flex h-[18px] w-[18px] shrink-0 items-center justify-center">
                      <span className="absolute h-[2px] w-[14px] rounded-full bg-gold" />
                      <motion.span
                        className="absolute h-[14px] w-[2px] rounded-full bg-gold"
                        animate={{ rotate: isOpen ? 90 : 0, opacity: isOpen ? 0 : 1 }}
                        transition={{ duration: 0.25, ease: EASE_OUT }}
                      />
                    </span>
                  </button>
                  <AnimatePresence initial={false}>
                    {isOpen && (
                      <motion.div
                        key="b"
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.32, ease: EASE_OUT }}
                        className="overflow-hidden"
                      >
                        <p className="px-6 pb-6 text-[15px] leading-relaxed text-dim">
                          {a}
                        </p>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}
