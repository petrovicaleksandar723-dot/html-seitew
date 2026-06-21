"use client";

import { Reveal, AnimatedHeading, Parallax, ParallaxY, ScrollScrub, stagger } from "@/components/award/ux";
import { Icon } from "@/components/cl/icons";
import { PILLS } from "@/lib/cl-data";
import { motion } from "framer-motion";

export function AwEditorial() {
  return (
    <section className="px-4 py-10 md:py-16">
      <div className="relative overflow-hidden rounded-[32px] bg-gradient-to-b from-[#faf6ec] to-[#ece3d0] px-6 py-24 text-center text-[#1c1812] md:px-12 md:py-36">
        {/* Decorative gold blur for depth */}
        <ParallaxY
          amount={60}
          dir={-1}
          className="pointer-events-none absolute -right-24 -top-24 z-0"
        >
          <div className="h-[420px] w-[420px] rounded-full bg-[radial-gradient(circle,rgba(196,154,74,0.22),transparent_70%)] blur-2xl" />
        </ParallaxY>

        <div className="relative z-10">
          <Reveal className="font-mono text-[12px] uppercase tracking-[0.2em] text-[#a07c33]">
            Kein Content-Stress mehr
          </Reveal>

          <ScrollScrub>
            <AnimatedHeading
              as="h2"
              lines={[
                "Du führst deinen Betrieb.",
                <span key="b">
                  Wir kümmern uns um{" "}
                  <span className="italic font-serif">deinen Content.</span>
                </span>,
              ]}
              className="mx-auto mt-6 max-w-[16ch] font-display text-[clamp(32px,6vw,84px)] font-extrabold leading-[1.0] tracking-[-0.03em] text-[#171307]"
            />
          </ScrollScrub>

          <Reveal delay={0.1}>
            <p className="mx-auto mt-7 max-w-[640px] text-[clamp(15px,1.4vw,19px)] text-[#5c513b]">
              Du bekommst jeden Monat fertige Ideen, Texte und Beiträge, die
              wirklich zu deinem Geschäft passen – ohne leere Phrasen, ohne
              Copy-Paste-Gefühl, ohne Zeitverschwendung.
            </p>
          </Reveal>

          <div className="mt-10 flex flex-wrap justify-center gap-3">
            {PILLS.map((p, i) => (
              <motion.span
                key={p.label}
                {...stagger(i)}
                className="inline-flex items-center gap-2.5 rounded-full border border-[rgba(138,109,46,0.3)] bg-white/60 px-5 py-3 font-semibold text-[#2a2110]"
              >
                <Icon name={p.icon} className="h-5 w-5 text-[#a07c33]" />
                {p.label}
              </motion.span>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
