"use client";

import { motion } from "framer-motion";
import { Reveal } from "@/components/ui/reveal";
import { DIAGNOSIS_METRICS, DIAGNOSIS_TAGS } from "@/lib/constants";

export function Diagnosis() {
  return (
    <section id="diagnose" className="py-[clamp(90px,14vw,170px)]">
      <div className="lightfield -left-40 top-20 h-[40vw] w-[40vw] bg-gold/[0.06]" />
      <div className="shell content relative z-10 grid items-center gap-14 lg:grid-cols-[1.05fr_0.95fr]">
        <div>
          <Reveal>
            <span className="eyebrow">Diagnose</span>
          </Reveal>
          <Reveal delay={0.05}>
            <h2 className="mt-6 font-display text-[clamp(32px,5vw,60px)] font-bold leading-[1.02] tracking-[-0.02em]">
              Gute Arbeit.
              <br />
              Aber online sieht man sie{" "}
              <span className="font-serif italic font-normal text-gold">
                nicht richtig.
              </span>
            </h2>
          </Reveal>
          <Reveal delay={0.12}>
            <p className="mt-6 max-w-[480px] font-body text-[17px] leading-relaxed text-dim">
              Viele Betriebe liefern jeden Tag starke Arbeit. Nur wirkt der
              Online-Auftritt oft nicht so hochwertig wie der Betrieb in echt.
            </p>
            <p className="mt-4 max-w-[480px] font-body text-[17px] leading-relaxed text-dim">
              Genau das ändern wir. Wir machen sichtbar, warum Kunden sich für
              dich entscheiden sollen — mit Content, der Vertrauen schafft,
              professionell aussieht und deine Leistung klar auf den Punkt
              bringt.
            </p>
          </Reveal>
        </div>

        <Reveal delay={0.15}>
          <div className="glass rounded-2xl p-8">
            <div className="font-mono text-[11px] uppercase tracking-[0.2em] text-muted">
              Status-Analyse
            </div>
            <div className="mt-6 space-y-6">
              {DIAGNOSIS_METRICS.map((m, i) => (
                <div key={m.label}>
                  <div className="flex items-baseline justify-between">
                    <span className="font-display text-[15px] font-bold text-ink">
                      {m.label}
                    </span>
                    <span className="font-mono text-[12px] text-gold/90">
                      {m.value}
                    </span>
                  </div>
                  <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-white/[0.06]">
                    <motion.div
                      initial={{ width: 0 }}
                      whileInView={{ width: `${m.level * 100}%` }}
                      viewport={{ once: true }}
                      transition={{
                        duration: 1.1,
                        delay: 0.2 + i * 0.15,
                        ease: [0.22, 1, 0.36, 1],
                      }}
                      className="h-full rounded-full bg-gradient-to-r from-gold-deep to-gold-bright"
                    />
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-8 h-px w-full bg-line" />
            <div className="mt-6 flex flex-wrap gap-2">
              {DIAGNOSIS_TAGS.map((t, i) => (
                <motion.span
                  key={t}
                  initial={{ opacity: 0, scale: 0.92 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  viewport={{ once: true }}
                  transition={{ delay: 0.4 + i * 0.08 }}
                  className="rounded-full border border-line bg-white/[0.02] px-3 py-1.5 font-body text-[12.5px] text-dim"
                >
                  {t}
                </motion.span>
              ))}
            </div>
          </div>
        </Reveal>
      </div>
    </section>
  );
}
