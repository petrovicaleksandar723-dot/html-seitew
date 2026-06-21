"use client";

import { motion, useReducedMotion } from "framer-motion";
import {
  Reveal,
  AnimatedHeading,
  Eyebrow,
  Button,
  stagger,
} from "@/components/cl/ui";
import { Icon } from "@/components/cl/icons";
import { PLANS, PAYS, MAIL } from "@/lib/cl-data";

export function ClPricing() {
  const reduce = useReducedMotion();

  return (
    <section id="pakete" className="relative px-5 py-16">
      <div className="mx-auto w-full max-w-[600px]">
        <Eyebrow>Monatspakete</Eyebrow>

        <AnimatedHeading
          as="h2"
          delay={0.05}
          className="mt-5 font-display text-[clamp(28px,8vw,42px)] font-extrabold leading-[1.08] tracking-[-0.025em]"
          lines={[
            <>Wähle, wie sichtbar dein</>,
            <>
              Betrieb werden <span className="text-gold">soll.</span>
            </>,
          ]}
        />

        <div className="mt-7 flex flex-col gap-4">
          {PLANS.map((plan, i) => (
            <motion.div
              key={plan.name}
              {...stagger(i)}
              whileHover={reduce ? undefined : { y: -5 }}
              transition={{ type: "spring", stiffness: 300, damping: 22 }}
            >
              <article
                className={`relative rounded-[22px] border border-line bg-gradient-to-b from-surface to-bg-2 p-6 ${
                  plan.featured
                    ? "border-gold/50 shadow-[0_20px_50px_rgba(216,178,116,0.14)]"
                    : ""
                }`}
              >
                {plan.featured && (
                  <span className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-gradient-to-br from-gold to-gold-bright px-4 py-1.5 text-[12px] font-extrabold uppercase tracking-[0.08em] text-[#1a1206]">
                    Beliebt
                  </span>
                )}

                <div className="grid h-[46px] w-[46px] place-items-center rounded-[13px] border border-gold/30 bg-gold/[0.12] text-gold-bright">
                  <Icon name={plan.icon} className="h-6 w-6" />
                </div>

                <h3 className="mt-3.5 font-display text-[20px] font-bold">
                  {plan.name}
                </h3>

                <div className="mt-1.5 flex items-baseline gap-1.5">
                  <b className="font-display text-[38px] font-extrabold text-gold-bright">
                    {plan.price}
                  </b>
                  <span className="text-[14px] text-dim">{plan.cadence}</span>
                </div>

                <p className="mt-2 text-[14px] text-dim">{plan.desc}</p>

                <ul className="my-5 flex flex-col gap-3">
                  {plan.features.map((feature, fi) => (
                    <motion.li
                      key={feature}
                      {...stagger(fi, 0.1)}
                      className="flex items-start gap-2.5 text-[14.5px]"
                    >
                      <Icon
                        name="check"
                        className="mt-0.5 h-5 w-5 flex-none text-gold"
                      />
                      {feature}
                    </motion.li>
                  ))}
                </ul>

                <Button
                  href={`mailto:${MAIL}?subject=${encodeURIComponent(
                    plan.name + " Paket"
                  )}`}
                  variant={plan.featured ? "primary" : "dark"}
                  className="mt-2 w-full"
                >
                  {plan.cta}
                </Button>
              </article>
            </motion.div>
          ))}
        </div>

        <Reveal delay={0.1} className="mt-7 text-center text-[12.5px] text-dim">
          🔒 Sichere Zahlung · monatlich kündbar · keine Einrichtungsgebühr
          <div className="mt-3 flex flex-wrap justify-center gap-2">
            {PAYS.map((pay) => (
              <span
                key={pay}
                className="rounded-[7px] border border-line bg-white/[0.03] px-2.5 py-1.5 text-[11px] font-bold text-dim"
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
