"use client";

import { motion } from "framer-motion";
import { Reveal } from "@/components/ui/reveal";
import { AnimatedHeading } from "@/components/ui/animated-heading";
import { CountUp } from "@/components/ui/count-up";
import { DIAGNOSIS_METRICS, DIAGNOSIS_TAGS } from "@/lib/constants";

const R = 52;
const CIRC = 2 * Math.PI * R;
const SCORE = 31; // overall visibility score

function Gauge() {
  return (
    <div className="relative grid h-[140px] w-[140px] flex-none place-items-center">
      <svg viewBox="0 0 140 140" className="h-full w-full -rotate-90">
        <circle cx="70" cy="70" r={R} fill="none" stroke="rgba(255,255,255,0.07)" strokeWidth="8" />
        <motion.circle
          cx="70"
          cy="70"
          r={R}
          fill="none"
          stroke="url(#gaugeGrad)"
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={CIRC}
          initial={{ strokeDashoffset: CIRC }}
          whileInView={{ strokeDashoffset: CIRC * (1 - SCORE / 100) }}
          viewport={{ once: true }}
          transition={{ duration: 1.6, ease: [0.22, 1, 0.36, 1], delay: 0.2 }}
        />
        <defs>
          <linearGradient id="gaugeGrad" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#a87f3e" />
            <stop offset="100%" stopColor="#f4d79e" />
          </linearGradient>
        </defs>
      </svg>
      <div className="absolute flex flex-col items-center">
        <CountUp
          to={SCORE}
          suffix="%"
          className="font-display text-[32px] font-extrabold tracking-tight"
        />
        <span className="font-mono text-[9px] uppercase tracking-[0.18em] text-muted">
          Sichtbarkeit
        </span>
      </div>
    </div>
  );
}

function Sparkline() {
  // weak, jagged "Anfragen" trend
  const d = "M0 40 L20 36 L40 42 L60 30 L80 34 L100 22 L120 26 L140 16";
  return (
    <div className="mt-7">
      <div className="flex items-baseline justify-between">
        <span className="font-mono text-[11px] uppercase tracking-[0.18em] text-muted">
          Anfragen / Woche
        </span>
        <span className="font-mono text-[11px] text-gold/80">
          <CountUp to={9} suffix=" / Ziel 40" />
        </span>
      </div>
      <svg viewBox="0 0 140 50" className="mt-3 h-16 w-full" preserveAspectRatio="none">
        <defs>
          <linearGradient id="spark" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="rgba(216,178,116,0.35)" />
            <stop offset="100%" stopColor="rgba(216,178,116,0)" />
          </linearGradient>
        </defs>
        <motion.path
          d={`${d} L140 50 L0 50 Z`}
          fill="url(#spark)"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 1, delay: 0.8 }}
        />
        <motion.path
          d={d}
          fill="none"
          stroke="#f4d79e"
          strokeWidth="1.6"
          strokeLinecap="round"
          strokeLinejoin="round"
          initial={{ pathLength: 0 }}
          whileInView={{ pathLength: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 1.4, ease: "easeInOut", delay: 0.4 }}
        />
        <motion.circle
          cx="140"
          cy="16"
          r="3"
          fill="#f4d79e"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ delay: 1.8 }}
        >
          <animate attributeName="r" values="3;5;3" dur="1.8s" repeatCount="indefinite" />
          <animate attributeName="opacity" values="1;0.4;1" dur="1.8s" repeatCount="indefinite" />
        </motion.circle>
      </svg>
    </div>
  );
}

export function Diagnosis() {
  return (
    <section id="diagnose" className="py-[clamp(90px,14vw,170px)]">
      <div className="lightfield -left-40 top-20 h-[40vw] w-[40vw] bg-gold/[0.06]" />
      <div className="shell content relative z-10 grid items-center gap-14 lg:grid-cols-[1.05fr_0.95fr]">
        <div>
          <Reveal>
            <span className="eyebrow">Diagnose</span>
          </Reveal>
          <AnimatedHeading
            className="mt-6 font-display text-[clamp(32px,5vw,60px)] font-bold leading-[1.02] tracking-[-0.02em]"
            lines={[
              [{ t: "Gute Arbeit." }],
              [{ t: "Aber online sieht man sie" }],
              [{ t: "nicht richtig.", accent: true }],
            ]}
          />
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
            <div className="flex items-center justify-between">
              <div className="font-mono text-[11px] uppercase tracking-[0.2em] text-muted">
                Status-Analyse
              </div>
              <span className="flex items-center gap-2 font-mono text-[10px] uppercase tracking-[0.2em] text-gold/90">
                <span className="relative flex h-1.5 w-1.5">
                  <span className="absolute h-1.5 w-1.5 animate-ping rounded-full bg-gold/70" />
                  <span className="h-1.5 w-1.5 rounded-full bg-gold" />
                </span>
                Live
              </span>
            </div>

            <div className="mt-6 flex items-center gap-7">
              <Gauge />
              <div className="flex-1 space-y-5">
                {DIAGNOSIS_METRICS.map((m, i) => (
                  <div key={m.label}>
                    <div className="flex items-baseline justify-between">
                      <span className="font-display text-[14px] font-bold text-ink">
                        {m.label}
                      </span>
                      <CountUp
                        to={Math.round(m.level * 100)}
                        suffix="%"
                        className="font-mono text-[12px] text-gold/90"
                      />
                    </div>
                    <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-white/[0.06]">
                      <motion.div
                        initial={{ width: 0 }}
                        whileInView={{ width: `${m.level * 100}%` }}
                        viewport={{ once: true }}
                        transition={{
                          duration: 1.1,
                          delay: 0.3 + i * 0.15,
                          ease: [0.22, 1, 0.36, 1],
                        }}
                        className="h-full rounded-full bg-gradient-to-r from-gold-deep to-gold-bright"
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <Sparkline />

            <div className="mt-7 h-px w-full bg-line" />
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
