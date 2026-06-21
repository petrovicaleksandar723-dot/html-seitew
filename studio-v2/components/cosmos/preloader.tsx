"use client";

import { useEffect, useState } from "react";
import { AnimatePresence, motion, useMotionValue, animate } from "framer-motion";
import { Icon } from "@/components/cl/icons";

const EASE = [0.76, 0, 0.24, 1] as const;

export function Preloader({ onEnter }: { onEnter: () => void }) {
  const [pct, setPct] = useState(0);
  const [ready, setReady] = useState(false);
  const [gone, setGone] = useState(false);
  const mv = useMotionValue(0);

  // self-driven, always-smooth progress (never sits stuck at 0%)
  useEffect(() => {
    const controls = animate(mv, 100, {
      duration: 2.1,
      ease: [0.4, 0, 0.1, 1],
      onUpdate: (v) => setPct(Math.round(v)),
      onComplete: () => setReady(true),
    });
    return () => controls.stop();
  }, [mv]);

  const enter = () => {
    setGone(true);
    onEnter();
  };

  return (
    <AnimatePresence>
      {!gone && (
        <motion.div
          className="fixed inset-0 z-[80] grid place-items-center bg-bg"
          exit={{ clipPath: "inset(0 0 100% 0)" }}
          transition={{ duration: 0.9, ease: EASE }}
        >
          {/* faint gold glow */}
          <div
            aria-hidden
            className="pointer-events-none absolute inset-0"
            style={{ background: "radial-gradient(50% 40% at 50% 45%, rgba(216,178,116,0.12), transparent 70%)" }}
          />
          <div className="relative w-[min(80vw,440px)] text-center">
            <motion.div
              initial={{ opacity: 0, y: 14 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, ease: EASE }}
              className="mb-10 flex flex-col items-center gap-3.5"
            >
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 14, repeat: Infinity, ease: "linear" }}
              >
                <Icon name="mark" className="h-14 w-14 text-gold" />
              </motion.div>
              <span className="font-display text-[18px] font-bold tracking-tight">
                CleanLines <span className="text-dim">Studio</span>
              </span>
              <span className="font-mono text-[10px] uppercase tracking-[0.3em] text-muted">
                Content · Cosmos
              </span>
            </motion.div>

            <div className="mb-2.5 flex items-end justify-between font-mono text-[11px] uppercase tracking-[0.2em] text-muted">
              <span>{ready ? "Bereit" : "Lädt Atelier"}</span>
              <span className="font-display text-[28px] font-extrabold tabular-nums text-ink">{pct}</span>
            </div>
            <div className="h-[2px] w-full overflow-hidden rounded-full bg-white/12">
              <motion.div
                className="h-full origin-left rounded-full bg-gradient-to-r from-gold-deep via-gold to-gold-bright"
                style={{ scaleX: pct / 100 }}
              />
            </div>

            <div className="mt-10 h-12">
              <AnimatePresence>
                {ready && (
                  <motion.button
                    initial={{ opacity: 0, y: 14 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, ease: EASE }}
                    onClick={enter}
                    data-magnetic
                    className="group inline-flex cursor-pointer items-center gap-2.5 rounded-full bg-gradient-to-br from-gold to-gold-bright px-8 py-4 font-display text-[15px] font-bold text-[#1a1206] shadow-[0_14px_40px_-12px_rgba(216,178,116,0.6)]"
                  >
                    Experience starten
                    <Icon name="arrow" className="h-4 w-4 transition-transform duration-300 group-hover:translate-x-1.5" />
                  </motion.button>
                )}
              </AnimatePresence>
            </div>
            <p className="mt-5 font-mono text-[10px] uppercase tracking-[0.2em] text-muted/70">
              Scroll baut die Szene auf
            </p>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
