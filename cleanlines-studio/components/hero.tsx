"use client";

import dynamic from "next/dynamic";
import { useRef } from "react";
import { motion, useScroll, useTransform } from "framer-motion";
import { MagneticButton } from "@/components/ui/magnetic";
import { CharHeading } from "@/components/ui/char-heading";
import { InView } from "@/components/ui/in-view";

const HeroCanvas = dynamic(() => import("@/components/scene/hero-canvas"), {
  ssr: false,
  loading: () => <CanvasFallback />,
});

function CanvasFallback() {
  return (
    <div className="absolute inset-0">
      <div className="lightfield left-1/2 top-1/3 h-[60vh] w-[60vh] -translate-x-1/2 bg-gold/20" />
    </div>
  );
}

const ease = [0.22, 1, 0.36, 1] as const;
// reveal after the preloader lifts (~1.85s)
const D = 1.9;

export function Hero() {
  const ref = useRef<HTMLElement>(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start start", "end start"],
  });

  const contentY = useTransform(scrollYProgress, [0, 1], [0, -160]);
  const contentOpacity = useTransform(scrollYProgress, [0, 0.6], [1, 0]);
  const contentBlur = useTransform(scrollYProgress, [0, 0.6], [0, 8]);
  const blurFilter = useTransform(contentBlur, (b) => `blur(${b}px)`);
  const canvasY = useTransform(scrollYProgress, [0, 1], [0, 120]);
  const canvasScale = useTransform(scrollYProgress, [0, 1], [1, 1.18]);

  return (
    <section
      ref={ref}
      id="hero"
      className="relative flex min-h-screen items-center pt-[72px]"
    >
      {/* WebGL stage */}
      <motion.div
        style={{ y: canvasY, scale: canvasScale }}
        className="absolute inset-0 z-0"
      >
        <InView fallback={<CanvasFallback />}>
          <HeroCanvas />
        </InView>
      </motion.div>

      {/* cinematic vignettes */}
      <div className="pointer-events-none absolute inset-0 z-[1] bg-[radial-gradient(120%_90%_at_50%_-10%,transparent_40%,#050505_100%)]" />
      <div className="pointer-events-none absolute inset-x-0 bottom-0 z-[1] h-40 bg-gradient-to-t from-bg to-transparent" />

      <motion.div
        style={{ y: contentY, opacity: contentOpacity, filter: blurFilter }}
        className="shell pointer-events-none relative z-10 w-full"
      >
        <div className="max-w-[820px]">
          <motion.span
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease, delay: D }}
            className="eyebrow"
          >
            Premium Content Studio
          </motion.span>

          <CharHeading
            as="h1"
            startDelay={D + 0.15}
            className="mt-6 font-display text-[clamp(44px,7.6vw,108px)] font-extrabold leading-[0.92] tracking-[-0.04em]"
            lines={[
              [{ t: "Dein Betrieb." }],
              [{ t: "Sichtbar wie eine" }],
              [{ t: "große Marke.", accent: true }],
            ]}
          />

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.9, ease, delay: D + 0.5 }}
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
            transition={{ duration: 0.9, ease, delay: D + 0.62 }}
            className="pointer-events-auto mt-10 flex flex-wrap items-center gap-4"
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
            transition={{ duration: 1, delay: D + 0.8 }}
            className="mt-7 font-mono text-[12px] uppercase tracking-[0.18em] text-muted"
          >
            Unverbindlich · persönlich · monatlich kündbar
          </motion.p>
        </div>
      </motion.div>

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
