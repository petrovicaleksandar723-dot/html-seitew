"use client";

import { useRef } from "react";
import { motion, useReducedMotion, useScroll, useTransform } from "framer-motion";
import { Icon } from "@/components/cl/icons";
import { LazyVideo } from "@/components/cl/ui";
import { HERO_VIDEO } from "@/lib/cl-data";

function Launcher() {
  return (
    <div className="absolute inset-0 flex flex-col items-center justify-center gap-1.5 bg-[radial-gradient(60%_50%_at_50%_45%,rgba(10,10,12,0.3),rgba(7,7,10,0.82))] p-5 text-center">
      <motion.div
        animate={{ y: [0, -7, 0] }}
        transition={{ duration: 4, repeat: Infinity, ease: [0.16, 1, 0.3, 1] }}
        className="mb-1.5 grid h-[74px] w-[74px] place-items-center rounded-[21px] border border-gold/40 bg-gradient-to-br from-[#1c1c22] to-[#0c0c10] text-gold-bright shadow-[0_14px_30px_rgba(0,0,0,0.5),inset_0_1px_0_rgba(255,255,255,0.06)]"
      >
        <Icon name="mark" className="h-10 w-10" />
      </motion.div>
      <h2 className="font-display text-[21px] font-extrabold tracking-tight">CleanLines Studio</h2>
      <p className="font-mono text-[12.5px] tracking-[0.05em] text-dim">Creative Content Hub</p>
      <div className="mt-5 flex flex-col items-center gap-2.5 font-mono text-[10.5px] font-bold uppercase tracking-[0.18em] text-gold">
        <span className="relative h-[34px] w-[22px] rounded-[12px] border-2 border-gold/60">
          <motion.span
            animate={{ y: [0, 12, 0], opacity: [0, 1, 0] }}
            transition={{ duration: 1.6, repeat: Infinity, ease: [0.16, 1, 0.3, 1] }}
            className="absolute left-1/2 top-1.5 h-1.5 w-[3px] -translate-x-1/2 rounded-full bg-gold"
          />
        </span>
        Scroll zum Starten
      </div>
    </div>
  );
}

export function Intro() {
  const ref = useRef<HTMLDivElement>(null);
  const reduce = useReducedMotion();
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start start", "end start"],
  });

  const scale = useTransform(scrollYProgress, [0, 1], [1, 9]);
  const launcherOpacity = useTransform(scrollYProgress, [0, 0.4], [1, 0]);
  const stageOpacity = useTransform(scrollYProgress, [0.8, 1], [1, 0]);
  const glow = useTransform(scrollYProgress, [0, 0.6], [0.2, 0]);

  if (reduce) {
    return (
      <div className="relative grid min-h-[100svh] place-items-center overflow-hidden px-6">
        <div className="relative aspect-[9/19] w-[min(266px,67vw)] rounded-[40px] border border-white/[0.16] bg-black p-[7px] shadow-[0_44px_90px_rgba(0,0,0,0.7)]">
          <div className="absolute left-1/2 top-[7px] z-[3] h-4 w-[32%] -translate-x-1/2 rounded-b-[12px] bg-black" />
          <div className="relative h-full w-full overflow-hidden rounded-[33px] bg-[#0a0a0c]">
            <LazyVideo src={HERO_VIDEO} eager className="h-full w-full object-cover opacity-50" />
            <Launcher />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div ref={ref} className="relative z-30 h-[230vh]">
      <motion.div
        style={{ opacity: stageOpacity }}
        className="sticky top-0 flex h-[100svh] items-center justify-center overflow-hidden"
      >
        <motion.div
          style={{ opacity: glow }}
          className="pointer-events-none absolute inset-0 bg-[radial-gradient(46%_36%_at_50%_42%,rgba(216,178,116,0.22),transparent_70%)]"
        />
        <motion.div
          style={{ scale, transformOrigin: "50% 44%" }}
          className="relative aspect-[9/19] w-[min(266px,67vw)] rounded-[40px] border border-white/[0.16] bg-black p-[7px] will-change-transform shadow-[0_44px_90px_rgba(0,0,0,0.7),0_0_0_1px_rgba(216,178,116,0.14),0_0_60px_rgba(216,178,116,0.12)]"
        >
          <div className="absolute left-1/2 top-[7px] z-[3] h-4 w-[32%] -translate-x-1/2 rounded-b-[12px] bg-black" />
          <div className="relative h-full w-full overflow-hidden rounded-[33px] bg-[#0a0a0c]">
            <LazyVideo src={HERO_VIDEO} eager className="h-full w-full object-cover opacity-50" />
            <motion.div style={{ opacity: launcherOpacity }} className="absolute inset-0">
              <Launcher />
            </motion.div>
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
}
