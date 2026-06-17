"use client";

import { motion } from "framer-motion";
import { Reveal } from "@/components/ui/reveal";
import { AnimatedHeading } from "@/components/ui/animated-heading";
import { MediaBackdrop } from "@/components/ui/media-backdrop";
import { MagneticButton } from "@/components/ui/magnetic";
import { asset } from "@/lib/asset";

const BG = [
  asset("/videos/example-1.mp4"),
  asset("/videos/example-2.mp4"),
  asset("/videos/example-3.mp4"),
  asset("/videos/example-4.mp4"),
];

export function FinalCta() {
  return (
    <section id="kontakt" className="py-[clamp(100px,16vw,200px)]">
      <MediaBackdrop videos={BG} opacity={0.14} />
      {/* cinematic closing glow + light trails */}
      <div className="lightfield left-1/2 top-1/2 z-[1] h-[50vw] w-[50vw] -translate-x-1/2 -translate-y-1/2 bg-gold/[0.09]" />
      <div className="pointer-events-none absolute inset-0 z-[1] opacity-40">
        {[0, 1, 2, 3].map((i) => (
          <motion.span
            key={i}
            className="absolute left-1/2 top-1/2 h-px w-[40vw] origin-left bg-gradient-to-r from-gold/50 to-transparent"
            style={{ rotate: `${i * 90 + 20}deg` }}
            animate={{ opacity: [0.15, 0.6, 0.15] }}
            transition={{ duration: 4, repeat: Infinity, delay: i * 0.6 }}
          />
        ))}
      </div>

      <div className="shell content relative z-10 text-center">
        <Reveal>
          <span className="eyebrow justify-center">Final Call</span>
        </Reveal>
        <AnimatedHeading
          className="mx-auto mt-6 max-w-[1000px] font-display text-[clamp(34px,6vw,78px)] font-extrabold leading-[1.0] tracking-[-0.035em]"
          lines={[
            [{ t: "Dein Betrieb kann aussehen wie eine Marke." }],
            [{ t: "Wir bauen den Content dafür.", accent: true }],
          ]}
        />
        <Reveal delay={0.14}>
          <p className="mx-auto mt-7 max-w-[560px] font-body text-[17px] leading-relaxed text-dim">
            Schick uns kurz deinen Betrieb und wir zeigen dir, welche Inhalte
            für dich funktionieren können — unverbindlich, direkt und ohne
            komplizierten Agenturprozess.
          </p>
        </Reveal>
        <Reveal delay={0.22}>
          <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
            <MagneticButton
              href="mailto:hallo@cleanlines.studio"
              variant="primary"
            >
              Kostenlose Einschätzung sichern
            </MagneticButton>
            <MagneticButton href="https://wa.me/" variant="ghost">
              WhatsApp-Anfrage starten
            </MagneticButton>
          </div>
        </Reveal>
        <Reveal delay={0.3}>
          <p className="mt-8 font-mono text-[12px] uppercase tracking-[0.18em] text-muted">
            Unverbindlich · klare Einschätzung · keine versteckten Kosten
          </p>
        </Reveal>
      </div>
    </section>
  );
}
