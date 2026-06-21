"use client";

import { motion } from "framer-motion";
import {
  Reveal,
  AnimatedHeading,
  Button,
  stagger,
  useHoverCapable,
  ParallaxY,
} from "@/components/award/ux";
import { Icon } from "@/components/cl/icons";
import { PLANS, PAYS, MAIL } from "@/lib/cl-data";

export function AwPricing() {
  const hover = useHoverCapable();

  return (
    <section id="pakete" className="py-24 md:py-32">
      <div className="mx-auto max-w-[1320px] px-5 sm:px-8">
        <Reveal className="text-center">
          <span className="block text-center font-mono text-[12px] uppercase tracking-[0.2em] text-gold">
            Monatspakete
          </span>
        </Reveal>

        <ParallaxY amount={16}>
          <AnimatedHeading
            as="h2"
            lines={[
              "Wähle, wie sichtbar dein",
              <span key="g" className="text-gold">
                Betrieb werden soll.
              </span>,
            ]}
            className="mx-auto mt-5 max-w-[20ch] text-center font-display text-[clamp(34px,5.5vw,64px)] font-extrabold leading-[1.04] tracking-[-0.03em]"
          />

          <Reveal delay={0.1}>
            <p className="mx-auto mt-5 max-w-[560px] text-center text-[clamp(15px,1.2vw,17px)] text-dim">
              Drei klare Pakete — je nachdem, ob du starten, wachsen oder deinen
              Auftritt auf Premium-Niveau bringen willst.
            </p>
          </Reveal>
        </ParallaxY>

        <div className="mt-16 grid items-center gap-6 lg:grid-cols-3">
          {PLANS.map((p, i) => (
            <ParallaxY key={p.name} amount={p.featured ? 18 : 50}>
            <motion.div
              {...stagger(i)}
              whileHover={hover && !p.featured ? { y: -6 } : undefined}
              className={`relative rounded-[24px] border bg-gradient-to-b from-surface to-bg-2 p-8 ${
                p.featured
                  ? "z-10 border-gold/50 shadow-[0_30px_80px_-30px_rgba(216,178,116,0.5)] lg:scale-[1.04]"
                  : "border-line"
              }`}
            >
              {p.featured && (
                <span className="absolute -top-3.5 left-1/2 -translate-x-1/2 rounded-full bg-gradient-to-br from-gold to-gold-bright px-4 py-1.5 text-[12px] font-extrabold uppercase tracking-[0.08em] text-[#1a1206]">
                  Beliebt
                </span>
              )}

              <div className="grid h-12 w-12 place-items-center rounded-2xl border border-gold/30 bg-gold/[0.12] text-gold-bright">
                <Icon name={p.icon} className="h-6 w-6" />
              </div>

              <h3 className="mt-4 font-display text-[22px] font-bold">{p.name}</h3>

              <div className="mt-2 flex items-baseline gap-1.5">
                <b className="font-display text-[44px] font-extrabold text-gold-bright">
                  {p.price}
                </b>
                <span className="text-[14px] text-dim">{p.cadence}</span>
              </div>

              <p className="mt-2 text-[14px] text-dim">{p.desc}</p>

              <ul className="my-7 flex flex-col gap-3.5 border-t border-line pt-7">
                {p.features.map((f, fi) => (
                  <motion.li
                    key={f}
                    {...stagger(fi, 0.1)}
                    className="flex items-start gap-3 text-[14.5px]"
                  >
                    <Icon name="check" className="mt-0.5 h-5 w-5 flex-none text-gold" />
                    {f}
                  </motion.li>
                ))}
              </ul>

              <Button
                href={`mailto:${MAIL}?subject=${encodeURIComponent(
                  p.name + " Paket"
                )}`}
                variant={p.featured ? "primary" : "dark"}
                className="w-full"
              >
                {p.cta}
              </Button>
            </motion.div>
            </ParallaxY>
          ))}
        </div>

        <Reveal className="mt-12 text-center">
          <p className="inline-flex items-center gap-2 text-[13px] text-dim">
            <span className="h-1.5 w-1.5 flex-none rounded-full bg-gold" />
            Sichere Zahlung · monatlich kündbar · keine Einrichtungsgebühr
          </p>
        </Reveal>

        <Reveal delay={0.05}>
          <div className="mt-4 flex flex-wrap justify-center gap-2.5">
            {PAYS.map((pay) => (
              <span
                key={pay}
                className="rounded-lg border border-line bg-white/[0.03] px-3 py-1.5 text-[11px] font-bold text-dim"
              >
                {pay}
              </span>
            ))}
          </div>
        </Reveal>
      </div>
    </section>
  );
}
