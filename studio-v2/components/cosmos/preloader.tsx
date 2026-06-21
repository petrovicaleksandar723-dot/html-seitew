"use client";

import { useEffect, useState } from "react";
import { useProgress } from "@react-three/drei";
import { AnimatePresence, motion } from "framer-motion";
import { Icon } from "@/components/cl/icons";

const EASE = [0.76, 0, 0.24, 1] as const;

export function Preloader({ onEnter }: { onEnter: () => void }) {
  const { progress, active } = useProgress();
  const [ready, setReady] = useState(false);
  const [gone, setGone] = useState(false);

  useEffect(() => {
    if (!active && progress >= 100) {
      const id = setTimeout(() => setReady(true), 300);
      return () => clearTimeout(id);
    }
  }, [active, progress]);

  // fail-safe: never trap the user
  useEffect(() => {
    const id = setTimeout(() => setReady(true), 6000);
    return () => clearTimeout(id);
  }, []);

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
          <div className="w-[min(78vw,420px)] text-center">
            <motion.div
              initial={{ opacity: 0, y: 14 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, ease: EASE }}
              className="mb-9 flex flex-col items-center gap-3"
            >
              <Icon name="mark" className="h-12 w-12 text-gold" />
              <span className="font-display text-[17px] font-bold tracking-tight">
                CleanLines <span className="text-dim">Studio</span>
              </span>
            </motion.div>
            <div className="mb-3 flex items-center justify-between font-mono text-[11px] uppercase tracking-[0.2em] text-muted">
              <span>Lädt</span>
              <span className="tabular-nums">{Math.round(progress)}%</span>
            </div>
            <div className="h-px w-full bg-white/15">
              <motion.div
                className="h-full bg-gradient-to-r from-gold-deep via-gold to-gold-bright"
                animate={{ width: `${progress}%` }}
                transition={{ ease: "linear" }}
              />
            </div>
            <div className="mt-9 h-12">
              <AnimatePresence>
                {ready && (
                  <motion.button
                    initial={{ opacity: 0, y: 12 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, ease: EASE }}
                    onClick={enter}
                    className="group inline-flex cursor-pointer items-center gap-2.5 rounded-full bg-gradient-to-br from-gold to-gold-bright px-7 py-3.5 font-display text-[14px] font-bold text-[#1a1206]"
                    data-magnetic
                  >
                    Experience starten
                    <Icon name="arrow" className="h-4 w-4 transition-transform duration-300 group-hover:translate-x-1" />
                  </motion.button>
                )}
              </AnimatePresence>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
