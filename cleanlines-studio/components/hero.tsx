"use client";

import dynamic from "next/dynamic";
import { motion } from "framer-motion";
import { MagneticButton } from "@/components/ui/magnetic";

const HeroCanvas = dynamic(() => import("@/components/scene/hero-canvas"), {
  ssr: false,
  loading: () => <CanvasFallback />,
});

function CanvasFallback() {
  return (
    <div className="absolute inset-0">
      <div className="lightfield h-[60vh] w-[60vh] left-1/2 top-1/3 -translate-x-1/2 bg-gold/20" />
    </div>
  );
}

const ease = [0.22, 1, 0.36, 1] as const;

export function Hero() {
  return (
    <section
      id="hero"
      className="relative flex min-h-screen items-center pt-[72px]"
    >
      {/* WebGL stage */}
      <div className="absolute inset-0 z-0">
        <HeroCanvas />
      </div>

      {/* cinematic vignettes */}
      <div className="pointer-events-none absolute inset-0 z-[1] bg-[radial-gradient(120%_90%_at_50%_-10%,transparent_40%,#050505_100%)]" />
      <div className="pointer-events-none absolute inset-x-0 bottom-0 z-[1] h-40 bg-gradient-to-t from-bg to-transparent" />

      <div className="shell relative z-10 w-full">
        <div className="max-w-[760px]">
          <motion.span
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease }}
            className="eyebrow"
          >
            Premium Content Studio
          </motion.span>

          <motion.h1
            initial={{ opacity: 0, y: 26 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, ease, delay: 0.08 }}
            className="mt-6 font-display text-[clamp(44px,7.4vw,104px)] font-extrabold leading-[0.94] tracking-[-0.035em]"
          >
            Dein Betrieb.
            <br />
            Sichtbar wie eine{" "}
            <span className="font-serif italic font-normal text-gradient-gold">
              große Marke.
            </span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.9, ease, delay: 0.2 }}
            className="mt-8 max-w-[560px] font-body text-[clamp(15px,1.5vw,18px)] leading-relaxed text-dim"
          >
            Wir erstellen hochwertige Reels, KI-Visuals und ein klares
            Content-System für lokale Betriebe, die online professioneller
            wirken, mehr Vertrauen aufbauen und aus Besuchern echte Anfragen
            machen wollen.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 18 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.9, ease, delay: 0.32 }}
            className="mt-10 flex flex-wrap items-center gap-4"
          >
            <MagneticButton href="#kontakt" variant="primary">
              Kostenlose Einschätzung sichern
            </MagneticButton>
            <MagneticButton href="#reel-cinema" variant="ghost">
              Beispiele ansehen
            </MagneticButton>
          </motion.div>

          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1, delay: 0.5 }}
            className="mt-7 font-mono text-[12px] uppercase tracking-[0.18em] text-muted"
          >
            Unverbindlich · persönlich · monatlich kündbar
          </motion.p>
        </div>
      </div>

      <div className="pointer-events-none absolute bottom-8 left-1/2 z-10 -translate-x-1/2">
        <motion.div
          animate={{ y: [0, 10, 0] }}
          transition={{ duration: 2.2, repeat: Infinity, ease: "easeInOut" }}
          className="font-mono text-[11px] uppercase tracking-[0.3em] text-muted"
        >
          Scroll
        </motion.div>
      </div>
    </section>
  );
}
