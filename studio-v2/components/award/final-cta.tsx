"use client";

import { motion } from "framer-motion";
import {
  Reveal,
  AnimatedHeading,
  Button,
  LazyVideo,
  stagger,
} from "@/components/award/ux";
import { Icon } from "@/components/cl/icons";
import { HERO_VIDEO, HERO_CHIPS, MAIL } from "@/lib/cl-data";

export function AwFinalCta() {
  return (
    <section className="relative overflow-hidden py-32 md:py-44">
      <LazyVideo
        src={HERO_VIDEO}
        className="absolute inset-0 h-full w-full object-cover opacity-[0.14]"
      />
      <div className="absolute inset-0 bg-[radial-gradient(60%_50%_at_50%_50%,rgba(216,178,116,0.14),transparent_70%)]" />
      <div className="absolute inset-0 bg-gradient-to-b from-bg via-bg/70 to-bg" />

      <div className="relative z-10 mx-auto max-w-[1320px] px-5 text-center sm:px-8">
        <Reveal>
          <span className="block text-center font-mono text-[12px] uppercase tracking-[0.2em] text-gold">
            Bereit für mehr Sichtbarkeit?
          </span>
        </Reveal>

        <AnimatedHeading
          as="h2"
          lines={[
            "Dein Betrieb muss nicht jeden",
            "Tag online kämpfen.",
            <span key="g" className="text-gold">
              Er braucht ein System.
            </span>,
          ]}
          className="mx-auto mt-6 max-w-[18ch] font-display text-[clamp(34px,6vw,82px)] font-extrabold leading-[1.0] tracking-[-0.035em]"
        />

        <Reveal delay={0.2}>
          <div className="mt-10 flex flex-wrap justify-center gap-4">
            <Button href={`mailto:${MAIL}`} variant="primary" magnetic>
              Kostenlose Content-Preview
              <Icon name="arrow" className="h-4 w-4" />
            </Button>
            <Button href="#pakete" variant="ghost">
              Pakete ansehen
            </Button>
          </div>
        </Reveal>

        <div className="mt-7 flex flex-wrap justify-center gap-2.5">
          {HERO_CHIPS.map((chip, i) => (
            <motion.span
              key={chip}
              {...stagger(i, 0.3)}
              className="rounded-full border border-line bg-white/[0.03] px-4 py-2 text-[12.5px] text-dim"
            >
              <Icon name="check" className="mr-1 inline h-3.5 w-3.5 text-gold" />
              {chip}
            </motion.span>
          ))}
        </div>
      </div>
    </section>
  );
}
