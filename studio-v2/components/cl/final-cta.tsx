"use client";

import { motion } from "framer-motion";
import { Reveal, AnimatedHeading, Eyebrow, Button, stagger } from "@/components/cl/ui";
import { MAIL } from "@/lib/cl-data";

const CHIPS = [
  "Kostenlose Preview",
  "Keine Mindestlaufzeit",
  "Monatlich kündbar",
  "Persönliche Beratung",
];

export function ClFinalCta() {
  return (
    <section className="relative overflow-hidden px-5 py-20 text-center">
      {/* soft champagne radial glow */}
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0"
        style={{
          background:
            "radial-gradient(60% 55% at 50% 38%, rgba(216,178,116,0.12), transparent 70%)",
        }}
      />

      <div className="relative mx-auto w-full max-w-[600px]">
        <div className="flex justify-center">
          <Eyebrow>Bereit für mehr Sichtbarkeit?</Eyebrow>
        </div>

        <AnimatedHeading
          as="h2"
          delay={0.05}
          className="mt-4 font-display text-[clamp(25px,7.5vw,36px)] font-extrabold leading-[1.12] tracking-[-0.02em]"
          lines={[
            <>Dein Betrieb muss nicht jeden</>,
            <>Tag online kämpfen.</>,
            <>
              Er braucht ein <span className="text-gold">System,</span>
            </>,
            <>das für dich arbeitet.</>,
          ]}
        />

        <Reveal delay={0.2}>
          <div className="mt-7 flex flex-col items-center gap-3">
            <Button href={`mailto:${MAIL}`} variant="primary">
              Kostenlose Content-Preview sichern
            </Button>
            <Button href="#pakete" variant="ghost">
              Pakete ansehen
            </Button>
          </div>
        </Reveal>

        <div className="mt-5 flex flex-wrap justify-center gap-2">
          {CHIPS.map((chip, i) => (
            <motion.span
              key={chip}
              {...stagger(i, 0.25)}
              className="rounded-full border border-line bg-white/[0.02] px-3 py-1.5 text-[12.5px] text-dim"
            >
              {chip}
            </motion.span>
          ))}
        </div>
      </div>
    </section>
  );
}
