"use client";

import { useState } from "react";
import { motion, AnimatePresence, useReducedMotion } from "framer-motion";
import { Reveal, AnimatedHeading, Eyebrow, EASE } from "@/components/cl/ui";
import { FAQ } from "@/lib/cl-data";

export function ClFaq() {
  const reduce = useReducedMotion();
  const [open, setOpen] = useState(0);

  return (
    <section id="faq" className="relative px-5 py-16">
      <div className="mx-auto w-full max-w-[600px]">
        <Eyebrow>FAQ</Eyebrow>

        <AnimatedHeading
          as="h2"
          delay={0.05}
          className="mt-5 font-display text-[clamp(28px,8vw,42px)] font-extrabold leading-[1.08] tracking-[-0.025em]"
          lines={[
            <>
              Häufige <span className="text-gold">Fragen.</span>
            </>,
          ]}
        />

        <Reveal delay={0.15} className="mt-6">
          <div className="flex flex-col gap-3">
            {FAQ.map((item, i) => {
              const isOpen = open === i;
              return (
                <div
                  key={item.q}
                  className={`overflow-hidden rounded-[16px] border bg-gradient-to-b from-surface to-bg-2 transition-colors ${
                    isOpen ? "border-gold/40" : "border-line"
                  }`}
                >
                  <button
                    type="button"
                    onClick={() => setOpen(isOpen ? -1 : i)}
                    aria-expanded={isOpen}
                    className="flex w-full items-center justify-between gap-4 px-[18px] py-[17px] text-left font-bold text-[15.5px]"
                  >
                    <span>{item.q}</span>

                    {/* plus / minus indicator */}
                    <span className="relative grid h-[18px] w-[18px] shrink-0 place-items-center text-gold">
                      {/* horizontal bar — always visible */}
                      <span className="absolute h-[2px] w-[13px] rounded-full bg-current" />
                      {/* vertical bar — rotates flat + fades out when open */}
                      <motion.span
                        className="absolute h-[13px] w-[2px] rounded-full bg-current"
                        initial={false}
                        animate={{ rotate: isOpen ? 90 : 0, opacity: isOpen ? 0 : 1 }}
                        transition={
                          reduce ? { duration: 0 } : { duration: 0.4, ease: EASE }
                        }
                      />
                    </span>
                  </button>

                  <AnimatePresence initial={false}>
                    {isOpen && (
                      <motion.div
                        key="body"
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={
                          reduce
                            ? { duration: 0 }
                            : { duration: 0.4, ease: EASE }
                        }
                        className="overflow-hidden"
                      >
                        <p className="px-[18px] pb-[18px] text-[14.5px] text-dim">
                          {item.a}
                        </p>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              );
            })}
          </div>
        </Reveal>
      </div>
    </section>
  );
}
