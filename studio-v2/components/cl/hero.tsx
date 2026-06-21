"use client";

import { motion, useReducedMotion } from "framer-motion";
import {
  Reveal,
  AnimatedHeading,
  Eyebrow,
  Button,
  CountUp,
  stagger,
  EASE,
} from "@/components/cl/ui";
import { STATS, HERO_CHIPS, MAIL } from "@/lib/cl-data";

export function ClHero() {
  const reduce = useReducedMotion();

  return (
    <section id="hero" className="relative px-5 pt-10 pb-16">
      {/* soft champagne glow behind the heading */}
      <div
        aria-hidden
        className="pointer-events-none absolute inset-x-0 top-0 -z-10 mx-auto h-[340px] max-w-[600px] bg-[radial-gradient(60%_55%_at_50%_18%,rgba(216,178,116,0.14),transparent_72%)]"
      />

      <div className="mx-auto w-full max-w-[600px] text-center">
        <div className="flex justify-center">
          <Eyebrow>Content-Service für lokale Betriebe</Eyebrow>
        </div>

        <AnimatedHeading
          as="h1"
          delay={0.05}
          className="mt-5 font-display text-[clamp(30px,9vw,46px)] font-extrabold leading-[1.08] tracking-[-0.025em]"
          lines={[
            "Regelmäßig posten.",
            "Ohne selbst ständig",
            <span key="gold" className="text-gold">
              Ideen zu suchen.
            </span>,
          ]}
        />

        <Reveal delay={0.15}>
          <p className="mx-auto mt-4 max-w-[440px] font-body text-[clamp(15px,4.2vw,17px)] text-dim">
            Wir erstellen dir jeden Monat fertige Reel-Ideen, Captions,
            Google-Beiträge und einen klaren Content-Plan – passend zu deinem
            Betrieb, deiner Zielgruppe und deinem Stil.
          </p>
        </Reveal>

        <Reveal delay={0.25}>
          <div className="mt-7 flex flex-col gap-3">
            <Button href={`mailto:${MAIL}`} variant="primary" magnetic>
              Kostenlose Content-Preview sichern
            </Button>
            <Button href="#pakete" variant="ghost">
              Pakete ansehen
            </Button>
          </div>
        </Reveal>

        {/* trust chips */}
        <div className="mt-5 flex flex-wrap justify-center gap-2">
          {HERO_CHIPS.map((chip, i) => (
            <motion.span
              key={chip}
              {...stagger(i, 0.35)}
              className="inline-flex items-center gap-1.5 rounded-full border border-line bg-white/[0.02] px-3 py-1.5 text-[12.5px] text-dim"
            >
              <span className="font-bold text-gold">✓</span>
              {chip}
            </motion.span>
          ))}
        </div>

        {/* stats */}
        <div className="mt-8 flex gap-2.5">
          {STATS.map((s, i) => (
            <motion.div
              key={s.label}
              {...stagger(i, 0.45)}
              whileHover={reduce ? undefined : { y: -4 }}
              transition={{ type: "spring", stiffness: 320, damping: 22 }}
              className="flex-1 rounded-[16px] border border-line bg-surface p-4 text-center transition-colors hover:border-gold/30"
            >
              <CountUp
                value={s.value}
                suffix={s.suffix}
                decimals={"decimals" in s ? (s.decimals ?? 0) : 0}
                className="font-display text-[clamp(20px,6vw,26px)] font-extrabold text-gold-bright"
              />
              <div className="mt-1 text-[11.5px] leading-snug text-dim">
                {s.label}
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
