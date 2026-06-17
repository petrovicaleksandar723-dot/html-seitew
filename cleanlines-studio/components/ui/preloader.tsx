"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence, useReducedMotion } from "framer-motion";
import { LogoMark } from "@/components/ui/logo";

export function Preloader() {
  const reduce = useReducedMotion();
  const [count, setCount] = useState(0);
  const [done, setDone] = useState(false);

  useEffect(() => {
    if (reduce) {
      setCount(100);
      setDone(true);
      return;
    }
    document.body.style.overflow = "hidden";
    const start = performance.now();
    const dur = 1500;
    let raf = 0;
    const tick = (now: number) => {
      const p = Math.min((now - start) / dur, 1);
      const eased = 1 - Math.pow(1 - p, 3);
      setCount(Math.round(eased * 100));
      if (p < 1) raf = requestAnimationFrame(tick);
      else setTimeout(() => setDone(true), 350);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [reduce]);

  useEffect(() => {
    if (done) document.body.style.overflow = "";
  }, [done]);

  return (
    <AnimatePresence>
      {!done && (
        <motion.div
          className="fixed inset-0 z-[100] flex flex-col items-center justify-center bg-bg"
          exit={{ y: "-100%" }}
          transition={{ duration: 0.9, ease: [0.76, 0, 0.24, 1] }}
        >
          <div className="lightfield h-[40vh] w-[40vh] bg-gold/10" />
          <motion.div
            initial={{ opacity: 0, scale: 0.85 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
            className="relative"
          >
            <LogoMark className="h-20 w-20 drop-shadow-[0_2px_30px_rgba(216,178,116,0.6)]" />
          </motion.div>

          <div className="relative mt-8 overflow-hidden">
            <motion.div
              initial={{ y: 30 }}
              animate={{ y: 0 }}
              transition={{ delay: 0.2, duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
              className="font-display text-[13px] font-medium tracking-[0.4em] text-ink"
            >
              CLEANLINES STUDIOS
            </motion.div>
          </div>

          <div className="absolute bottom-10 right-10 font-display text-[clamp(40px,8vw,90px)] font-extrabold tabular-nums leading-none text-ink/90">
            {count}
            <span className="text-gold">%</span>
          </div>

          <div className="absolute bottom-0 left-0 h-px w-full bg-line">
            <motion.div
              className="h-full origin-left bg-gradient-to-r from-gold-deep via-gold to-gold-bright"
              style={{ scaleX: count / 100 }}
            />
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
