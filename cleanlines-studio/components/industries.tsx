"use client";

import { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Reveal } from "@/components/ui/reveal";
import { AnimatedHeading } from "@/components/ui/animated-heading";
import { INDUSTRIES } from "@/lib/constants";
import { asset } from "@/lib/asset";

const VIDEOS = [
  asset("/videos/brand-particles.mp4"),
  asset("/videos/brand-studio.mp4"),
  asset("/videos/brand-streaks.mp4"),
  asset("/videos/brand-gold-flow.mp4"),
];

export function Industries() {
  const [active, setActive] = useState(0);
  const [paused, setPaused] = useState(false);
  const timer = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    if (paused) return;
    timer.current = setInterval(
      () => setActive((a) => (a + 1) % INDUSTRIES.length),
      4200
    );
    return () => {
      if (timer.current) clearInterval(timer.current);
    };
  }, [paused]);

  const cur = INDUSTRIES[active];
  const video = VIDEOS[active % VIDEOS.length];

  return (
    <section id="branchen" className="py-[clamp(90px,14vw,170px)]">
      <div className="shell content relative z-10">
        <Reveal>
          <span className="eyebrow">Branchen</span>
        </Reveal>
        <AnimatedHeading
          className="mt-6 max-w-[760px] font-display text-[clamp(32px,5vw,60px)] font-bold leading-[1.02] tracking-[-0.02em]"
          lines={[
            [{ t: "Content, der zu deinem" }],
            [{ t: "Betrieb passt.", accent: true }],
          ]}
        />
        <Reveal delay={0.1}>
          <p className="mt-6 max-w-[640px] font-body text-[17px] leading-relaxed text-dim">
            Jede Branche verkauft anders. Wähle deinen Bereich — Tonalität,
            Formate und Visuals passen sich an.
          </p>
        </Reveal>

        <div
          className="mt-14 grid gap-8 lg:grid-cols-[0.8fr_1.2fr]"
          onMouseEnter={() => setPaused(true)}
          onMouseLeave={() => setPaused(false)}
        >
          {/* selector list */}
          <div className="flex flex-col">
            {INDUSTRIES.map((ind, i) => {
              const on = i === active;
              return (
                <button
                  key={ind.title}
                  data-hot
                  onMouseEnter={() => setActive(i)}
                  onFocus={() => setActive(i)}
                  onClick={() => setActive(i)}
                  className="group relative border-b border-line py-5 text-left"
                >
                  <div className="flex items-center gap-4">
                    <span
                      className="font-mono text-[12px] tabular-nums transition-colors"
                      style={{ color: on ? ind.accent : "#6e6a62" }}
                    >
                      {String(i + 1).padStart(2, "0")}
                    </span>
                    <span
                      className={`font-display text-[clamp(20px,2.4vw,30px)] font-bold tracking-tight transition-all duration-300 ${
                        on ? "text-ink" : "text-muted group-hover:text-dim"
                      }`}
                      style={{ paddingLeft: on ? 8 : 0 }}
                    >
                      {ind.title}
                    </span>
                  </div>
                  {on && (
                    <motion.span
                      layoutId="ind-bar"
                      className="absolute -bottom-px left-0 h-[2px] w-full"
                      style={{
                        background: `linear-gradient(90deg, ${ind.accent}, transparent)`,
                      }}
                    />
                  )}
                </button>
              );
            })}
          </div>

          {/* morphing stage */}
          <div className="relative min-h-[420px] overflow-hidden rounded-2xl border border-line lg:min-h-[520px]">
            <AnimatePresence mode="wait">
              <motion.div
                key={active}
                initial={{ opacity: 0, scale: 1.04 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.99 }}
                transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
                className="absolute inset-0"
              >
                <video
                  className="h-full w-full object-cover"
                  src={video}
                  autoPlay
                  muted
                  loop
                  playsInline
                  preload="metadata"
                />
                <div
                  className="absolute inset-0"
                  style={{
                    background: `linear-gradient(180deg, ${cur.accent}14 0%, rgba(5,5,5,0.2) 40%, rgba(5,5,5,0.92) 100%)`,
                  }}
                />
              </motion.div>
            </AnimatePresence>

            {/* foreground content (stable, crossfades text) */}
            <div className="relative z-10 flex h-full min-h-[420px] flex-col justify-end p-8 lg:min-h-[520px]">
              <AnimatePresence mode="wait">
                <motion.div
                  key={active}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -12 }}
                  transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
                >
                  <span
                    className="font-mono text-[11px] uppercase tracking-[0.22em]"
                    style={{ color: cur.accent }}
                  >
                    Branche {String(active + 1).padStart(2, "0")} /{" "}
                    {String(INDUSTRIES.length).padStart(2, "0")}
                  </span>
                  <h3 className="mt-3 font-display text-[clamp(28px,4vw,46px)] font-extrabold tracking-tight">
                    {cur.title}
                  </h3>
                  <p className="mt-3 max-w-[440px] font-body text-[15px] leading-relaxed text-dim">
                    {cur.body}
                  </p>
                </motion.div>
              </AnimatePresence>

              {/* progress ticks */}
              <div className="mt-7 flex gap-1.5">
                {INDUSTRIES.map((_, i) => (
                  <span
                    key={i}
                    className="h-1 flex-1 overflow-hidden rounded-full bg-white/10"
                  >
                    {i === active && !paused && (
                      <motion.span
                        className="block h-full"
                        style={{ background: cur.accent }}
                        initial={{ width: "0%" }}
                        animate={{ width: "100%" }}
                        transition={{ duration: 4.2, ease: "linear" }}
                      />
                    )}
                    {i < active && (
                      <span
                        className="block h-full w-full"
                        style={{ background: `${cur.accent}99` }}
                      />
                    )}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
