"use client";

import { motion, useReducedMotion } from "framer-motion";
import {
  Reveal,
  AnimatedHeading,
  Button,
  stagger,
  SPRING,
  useHoverCapable,
  ParallaxY,
} from "@/components/award/ux";
import { Icon } from "@/components/cl/icons";
import { EINZEL, MAIL } from "@/lib/cl-data";

function EinzelCard({ item, i }: { item: (typeof EINZEL)[number]; i: number }) {
  const hover = useHoverCapable();
  const reduce = useReducedMotion();
  const lift = hover && !reduce;

  return (
    <ParallaxY amount={i % 2 === 0 ? 28 : 58}>
    <motion.article
      {...stagger(i)}
      whileHover={lift ? { y: -6 } : undefined}
      transition={SPRING}
      className="group relative h-full cursor-pointer overflow-hidden rounded-[22px] border border-line bg-gradient-to-b from-surface to-bg-2 p-7 transition-colors duration-300 hover:border-gold/30 md:p-8"
    >
      <span
        aria-hidden
        className="pointer-events-none absolute -right-12 -top-12 h-44 w-44 rounded-full bg-[radial-gradient(circle,rgba(216,178,116,0.08),transparent_70%)] opacity-0 blur-xl transition-opacity duration-300 group-hover:opacity-100"
      />

      <div className="relative z-10">
        <div className="grid h-12 w-12 place-items-center rounded-2xl border border-gold/30 bg-gold/[0.12] text-gold-bright transition-transform duration-300 ease-out group-hover:scale-105 group-hover:-rotate-3">
          <Icon name={item.icon as never} className="h-6 w-6" />
        </div>

        <div className="mt-6 flex items-start justify-between gap-4">
          <h3 className="font-display text-[clamp(20px,1.7vw,26px)] font-bold leading-tight">
            {item.title}
          </h3>
          <span className="rounded-full border border-gold/30 bg-gold/[0.1] px-3.5 py-1.5 font-display text-[14px] font-extrabold text-gold whitespace-nowrap">
            {item.tag}
          </span>
        </div>

        <p className="mt-3 text-[15px] text-dim leading-relaxed">{item.body}</p>
      </div>
    </motion.article>
    </ParallaxY>
  );
}

export function AwEinzel() {
  return (
    <section className="relative mx-auto max-w-[1320px] px-5 py-24 sm:px-8 md:py-32">
      <ParallaxY amount={20}>
      <div className="font-mono text-[12px] uppercase tracking-[0.2em] text-gold">
        Einzelaufträge
      </div>

      <AnimatedHeading
        as="h2"
        lines={[
          <span key="a">
            Du brauchst <span className="text-gold">mehr</span> als Content?
          </span>,
        ]}
        className="mt-5 font-display text-[clamp(34px,5.5vw,68px)] font-extrabold leading-[1.02] tracking-[-0.03em]"
      />

      <Reveal delay={0.1}>
        <p className="mt-5 max-w-[560px] text-[clamp(15px,1.2vw,17px)] text-dim">
          Für einzelne Projekte bekommst du klare Festpreise, saubere Umsetzung
          und ein Ergebnis, das professionell wirkt.
        </p>
      </Reveal>
      </ParallaxY>

      <div className="mt-14 grid gap-5 md:grid-cols-2">
        {EINZEL.map((item, i) => (
          <EinzelCard key={item.title} item={item} i={i} />
        ))}
      </div>

      <Reveal delay={0.1}>
        <div className="mt-12 flex justify-center">
          <Button
            href={`mailto:${MAIL}?subject=Einzelauftrag%20Anfrage`}
            variant="primary"
            magnetic
          >
            Projekt anfragen <Icon name="arrow" className="h-4 w-4" />
          </Button>
        </div>
      </Reveal>
    </section>
  );
}
