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
import { EINZEL, MAIL } from "@/lib/cl-data";

export function ClEinzel() {
  const reduce = useReducedMotion();

  return (
    <section className="relative px-5 py-16">
      <div className="mx-auto w-full max-w-[600px]">
        <Eyebrow>Einzelaufträge</Eyebrow>
        <AnimatedHeading
          as="h2"
          className="mt-4 font-display text-[30px] font-extrabold leading-[1.08] tracking-tight"
          lines={["Du brauchst mehr als Content?"]}
        />
        <Reveal delay={0.1}>
          <p className="mt-4 text-[15px] text-dim">
            Für einzelne Projekte bekommst du klare Festpreise, saubere Umsetzung
            und ein Ergebnis, das professionell wirkt.
          </p>
        </Reveal>

        <div className="mt-7 flex flex-col gap-3.5">
          {EINZEL.map((item, i) => (
            <motion.article
              key={item.title}
              {...stagger(i)}
              whileHover={reduce ? undefined : { y: -4 }}
              transition={{ type: "spring", stiffness: 300, damping: 22 }}
              className="group rounded-[18px] border border-line bg-gradient-to-b from-surface to-bg-2 p-5 transition-colors duration-300 will-change-transform hover:border-gold/30"
            >
              <div className="grid h-[46px] w-[46px] place-items-center rounded-[13px] border border-gold/30 bg-gold/[0.12] text-gold-bright">
                <Icon name={item.icon} className="h-6 w-6" />
              </div>
              <h3 className="mt-3.5 font-display text-[18px] font-bold">
                {item.title}
              </h3>
              <span className="mt-1.5 inline-block rounded-full border border-gold/30 bg-gold/[0.1] px-3 py-1 font-display text-[14px] font-extrabold text-gold">
                {item.tag}
              </span>
              <p className="mt-2 text-[14px] text-dim">{item.body}</p>
            </motion.article>
          ))}
        </div>

        <Reveal delay={0.05} className="mt-6 flex justify-center">
          <Button
            href={`mailto:${MAIL}?subject=Einzelauftrag%20Anfrage`}
            variant="primary"
          >
            Projekt anfragen
          </Button>
        </Reveal>
      </div>
    </section>
  );
}
