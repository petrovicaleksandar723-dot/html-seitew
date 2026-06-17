"use client";

import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Reveal } from "@/components/ui/reveal";
import { AnimatedHeading } from "@/components/ui/animated-heading";
import { TRUST, FAQ } from "@/lib/constants";

function Item({
  q,
  a,
  open,
  onToggle,
}: {
  q: string;
  a: string;
  open: boolean;
  onToggle: () => void;
}) {
  return (
    <div className="border-b border-line">
      <button
        onClick={onToggle}
        aria-expanded={open}
        className="flex w-full items-center justify-between gap-4 py-5 text-left"
      >
        <span className="font-display text-[16.5px] font-bold tracking-tight text-ink">
          {q}
        </span>
        <span
          className={`grid h-7 w-7 flex-none place-items-center rounded-full border border-line text-gold transition-transform duration-300 ${
            open ? "rotate-45" : ""
          }`}
        >
          +
        </span>
      </button>
      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
            className="overflow-hidden"
          >
            <p className="pb-5 font-body text-[14.5px] leading-relaxed text-dim">
              {a}
            </p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export function Faq() {
  const [open, setOpen] = useState<number | null>(0);

  return (
    <section className="py-[clamp(90px,14vw,170px)]">
      <div className="shell content relative z-10 grid gap-14 lg:grid-cols-[0.85fr_1.15fr]">
        <div>
          <Reveal>
            <span className="eyebrow">Trust</span>
          </Reveal>
          <AnimatedHeading
            className="mt-6 font-display text-[clamp(30px,4.4vw,52px)] font-bold leading-[1.03] tracking-[-0.02em]"
            lines={[
              [{ t: "Klarer Content." }],
              [{ t: "Kein Agentur-Blabla.", accent: true }],
            ]}
          />
          <Reveal delay={0.1}>
            <p className="mt-6 max-w-[380px] font-body text-[16px] leading-relaxed text-dim">
              Du bekommst keine komplizierten Strategien, die am Ende keiner
              umsetzt. Du bekommst klare Inhalte, klare Abläufe und Content, der
              deinen Betrieb hochwertig zeigt.
            </p>
            <ul className="mt-8 space-y-3">
              {TRUST.map((t) => (
                <li
                  key={t}
                  className="flex items-start gap-3 font-body text-[14.5px] text-ink"
                >
                  <span className="mt-0.5 text-gold">✓</span>
                  {t}
                </li>
              ))}
            </ul>
          </Reveal>
        </div>

        <Reveal delay={0.1}>
          <div className="mx-auto w-full max-w-[720px]">
            {FAQ.map((f, i) => (
              <Item
                key={f.q}
                q={f.q}
                a={f.a}
                open={open === i}
                onToggle={() => setOpen(open === i ? null : i)}
              />
            ))}
          </div>
        </Reveal>
      </div>
    </section>
  );
}
