"use client";

import { useRef } from "react";
import { motion, useReducedMotion } from "framer-motion";
import {
  Reveal,
  AnimatedHeading,
  Button,
  CountUp,
  LazyVideo,
  Phone,
  ParallaxY,
  useExitOnScroll,
  stagger,
  EASE_IN_OUT,
} from "@/components/award/ux";
import { Icon } from "@/components/cl/icons";
import { STATS, HERO_VIDEO, MAIL } from "@/lib/cl-data";

export function AwHero() {
  const reduce = useReducedMotion();
  const sectionRef = useRef<HTMLElement>(null);
  const exit = useExitOnScroll(sectionRef);

  const float = (distance: number, duration: number) =>
    reduce
      ? undefined
      : {
          animate: { y: [0, -distance, 0] },
          transition: { duration, ease: EASE_IN_OUT, repeat: Infinity },
        };

  return (
    <section
      ref={sectionRef}
      className="relative flex min-h-screen items-center overflow-hidden pt-32 pb-20"
    >
      {/* ambient backdrop */}
      <div
        aria-hidden
        className="pointer-events-none absolute -top-1/4 right-[-10%] h-[80vh] w-[80vh] rounded-full bg-gold/[0.07] blur-[140px]"
      />

      <motion.div
        style={exit}
        className="mx-auto grid w-full max-w-[1320px] grid-cols-1 items-center gap-12 px-5 sm:px-8 lg:grid-cols-[1.15fr_0.85fr] lg:gap-8"
      >
        {/* ---------------------------------------------------------- LEFT */}
        <ParallaxY amount={26} className="relative z-[2]">
          <Reveal y={10}>
            <span className="font-mono text-[12px] uppercase tracking-[0.2em] text-gold">
              Content-Studio für lokale Betriebe
            </span>
          </Reveal>

          <AnimatedHeading
            as="h1"
            delay={0.05}
            lines={[
              "Regelmäßig posten.",
              "Ohne selbst ständig",
              <span key="g" className="text-gold">
                Ideen zu suchen.
              </span>,
            ]}
            className="mt-6 font-display text-[clamp(40px,7vw,96px)] font-extrabold leading-[0.98] tracking-[-0.04em]"
          />

          <Reveal delay={0.2}>
            <p className="mt-7 max-w-[540px] font-body text-[clamp(16px,1.3vw,18px)] leading-relaxed text-dim">
              Wir erstellen dir jeden Monat fertige Reel-Ideen, Captions,
              Google-Beiträge und einen klaren Content-Plan – passend zu deinem
              Betrieb, deiner Zielgruppe und deinem Stil.
            </p>
          </Reveal>

          <Reveal delay={0.3}>
            <div className="mt-9 flex flex-wrap gap-4">
              <Button href={`mailto:${MAIL}`} variant="primary" magnetic>
                Kostenlose Content-Preview
                <Icon name="arrow" className="h-4 w-4" />
              </Button>
              <Button href="#pakete" variant="ghost">
                Pakete ansehen
              </Button>
            </div>
          </Reveal>

          {/* stats */}
          <div className="mt-12 flex flex-wrap items-end gap-8 md:gap-12">
            {STATS.map((s, i) => (
              <motion.div key={s.label} className="flex items-end gap-8 md:gap-12" {...stagger(i, 0.35)}>
                {i > 0 && (
                  <span
                    aria-hidden
                    className="h-10 w-px bg-gradient-to-b from-transparent via-line to-transparent"
                  />
                )}
                <div>
                  <CountUp
                    value={s.value}
                    suffix={s.suffix}
                    decimals={"decimals" in s ? s.decimals : 0}
                    className="font-display text-[clamp(28px,3vw,44px)] font-extrabold text-gold-bright"
                  />
                  <div className="mt-1 font-mono text-[11px] uppercase tracking-[0.14em] text-muted">
                    {s.label}
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </ParallaxY>

        {/* --------------------------------------------------------- RIGHT */}
        <div className="relative grid place-items-center">
          {/* gold radial glow */}
          <ParallaxY
            amount={120}
            dir={-1}
            className="pointer-events-none absolute h-[120%] w-[120%]"
          >
            <div
              aria-hidden
              className="h-full w-full rounded-full bg-[radial-gradient(circle,rgba(216,178,116,0.18),transparent_62%)] blur-2xl"
            />
          </ParallaxY>

          <ParallaxY amount={70} className="relative">
            <motion.div {...(float(12, 5) ?? {})}>
              <Phone width={300} live>
                <LazyVideo
                  src={HERO_VIDEO}
                  eager
                  className="h-full w-full object-cover opacity-90"
                />
              </Phone>
            </motion.div>
          </ParallaxY>

          {/* floating glass chips */}
          <ParallaxY
            amount={110}
            dir={-1}
            className="absolute left-0 top-10 z-[3] sm:-left-2 lg:left-[-4%]"
          >
            <Reveal y={14} delay={0.55}>
              <motion.div
                {...(float(8, 6) ?? {})}
                className="flex items-center gap-2 rounded-2xl border border-line bg-bg/70 px-4 py-2.5 text-[13px] font-semibold text-ink shadow-xl backdrop-blur"
              >
                <Icon name="growth" className="h-4 w-4 text-gold-bright" />
                +128% Reichweite
              </motion.div>
            </Reveal>
          </ParallaxY>

          <ParallaxY
            amount={50}
            className="absolute bottom-12 right-0 z-[3] sm:-right-2 lg:right-[-4%]"
          >
            <Reveal y={14} delay={0.7}>
              <motion.div
                {...(float(10, 6.8) ?? {})}
                className="flex items-center gap-2 rounded-2xl border border-line bg-bg/70 px-4 py-2.5 text-[13px] font-semibold text-ink shadow-xl backdrop-blur"
              >
                <Icon name="check" className="h-4 w-4 text-gold-bright" />
                Reel-Idee
              </motion.div>
            </Reveal>
          </ParallaxY>
        </div>
      </motion.div>

      {/* scroll cue */}
      <div className="pointer-events-none absolute bottom-6 left-1/2 hidden -translate-x-1/2 flex-col items-center gap-2 md:flex">
        <span className="relative h-9 w-px overflow-hidden bg-line">
          {!reduce && (
            <motion.span
              className="absolute inset-x-0 top-0 h-3 bg-gold"
              animate={{ y: ["-100%", "300%"] }}
              transition={{ duration: 1.8, ease: EASE_IN_OUT, repeat: Infinity }}
            />
          )}
        </span>
        <span className="font-mono text-[10px] uppercase tracking-[0.3em] text-muted">
          Scroll
        </span>
      </div>
    </section>
  );
}
