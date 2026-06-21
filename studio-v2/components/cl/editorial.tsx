"use client";

import { motion } from "framer-motion";
import { Reveal, AnimatedHeading, Eyebrow, stagger } from "@/components/cl/ui";
import { Icon } from "@/components/cl/icons";
import { PILLS } from "@/lib/cl-data";

export function ClEditorial() {
  return (
    <section className="relative px-1.5 py-6">
      <div className="mx-2.5 rounded-[28px] bg-gradient-to-b from-[#faf6ec] to-[#ece3d0] px-6 py-12 text-[#1c1812]">
        <div className="mx-auto w-full max-w-[560px] text-center">
          <Eyebrow dark>Kein Content-Stress mehr</Eyebrow>

          <AnimatedHeading
            as="h2"
            delay={0}
            className="mt-4 font-display text-[clamp(25px,7.5vw,38px)] font-extrabold leading-[1.1] tracking-[-0.02em] text-[#171307]"
            lines={[
              "Du führst deinen Betrieb.",
              "Wir kümmern uns um deinen Content.",
            ]}
          />

          <Reveal delay={0.1}>
            <p className="mt-4 text-[clamp(15px,4.2vw,17px)] text-[#5c513b]">
              Du bekommst jeden Monat fertige Ideen, Texte und Beiträge, die
              wirklich zu deinem Geschäft passen – ohne leere Phrasen, ohne
              Copy-Paste-Gefühl, ohne Zeitverschwendung.
            </p>
          </Reveal>

          <div className="mt-6 flex flex-col gap-2.5 text-left">
            {PILLS.map((pill, i) => (
              <motion.div
                key={pill.label}
                {...stagger(i)}
                className="flex items-center gap-3 rounded-[14px] border border-[rgba(138,109,46,0.25)] bg-white/55 px-4 py-3.5 font-semibold text-[#2a2110]"
              >
                <Icon
                  name={pill.icon}
                  className="h-[22px] w-[22px] flex-none text-[#a07c33]"
                />
                {pill.label}
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
