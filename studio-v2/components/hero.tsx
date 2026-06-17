"use client";

import { useRef } from "react";
import { motion, useReducedMotion, useScroll, useTransform } from "framer-motion";
import { IMG } from "@/lib/content";

const ease = [0.16, 1, 0.3, 1] as const;

export function Hero() {
  const ref = useRef<HTMLDivElement>(null);
  const reduce = useReducedMotion();
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start start", "end start"],
  });

  const imgScale = useTransform(scrollYProgress, [0, 1], [1, 1.1]);
  const imgY = useTransform(scrollYProgress, [0, 1], ["0%", "12%"]);
  const overlayY = useTransform(scrollYProgress, [0, 1], ["0%", "-26%"]);
  const fade = useTransform(scrollYProgress, [0, 0.7], [1, 0]);

  return (
    <section id="top" ref={ref} className="relative h-[100svh] min-h-[640px] w-full overflow-hidden">
      {/* 4K image layer */}
      <motion.div
        className="absolute inset-0"
        style={reduce ? undefined : { scale: imgScale, y: imgY }}
      >
        <img
          src={IMG.hero}
          alt="Clean Lines Studios — kreatives Content-Studio im goldenen Licht"
          className="h-full w-full object-cover"
          // eslint-disable-next-line @next/next/no-img-element
          fetchPriority="high"
        />
      </motion.div>

      {/* gradients for legibility */}
      <div className="absolute inset-0 bg-gradient-to-b from-bg/55 via-bg/20 to-bg" />
      <div className="absolute inset-0 bg-gradient-to-r from-bg/70 via-transparent to-transparent" />

      {/* copy */}
      <motion.div
        className="relative z-10 flex h-full flex-col justify-end pb-[10vh]"
        style={reduce ? undefined : { y: overlayY, opacity: fade }}
      >
        <div className="shell" style={{ ["--max" as string]: "1680px" }}>
          <motion.span
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease }}
            className="eyebrow"
          >
            Content-Studio · für lokale Betriebe
          </motion.span>

          <h1 className="mt-6 max-w-[16ch] font-display text-[clamp(44px,8vw,118px)] font-extrabold leading-[0.95] tracking-[-0.03em]">
            {["Deine Arbeit", "verdient den"].map((line, i) => (
              <motion.span
                key={line}
                initial={{ opacity: 0, y: 40 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 1, ease, delay: 0.1 + i * 0.12 }}
                className="block"
              >
                {line}
              </motion.span>
            ))}
            <motion.span
              initial={{ opacity: 0, y: 40 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 1, ease, delay: 0.34 }}
              className="block font-serif italic text-gold"
            >
              besten Auftritt.
            </motion.span>
          </h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.9, ease, delay: 0.5 }}
            className="mt-7 max-w-[440px] font-body text-[clamp(15px,1.5vw,18px)] leading-relaxed text-dim"
          >
            Wir produzieren Reels, Fotos und einen Online-Auftritt, der so
            hochwertig wirkt wie dein Betrieb in echt.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.9, ease, delay: 0.62 }}
            className="mt-9 flex flex-wrap items-center gap-4"
          >
            <a
              href="#kontakt"
              className="rounded-full bg-gradient-to-br from-gold-bright to-gold-deep px-7 py-3.5 font-display text-[15px] font-bold text-[#1a1206] shadow-[0_18px_50px_-16px_rgba(216,178,116,0.7)] transition-transform duration-300 hover:scale-[1.03]"
            >
              Projekt starten
            </a>
            <a
              href="#leistungen"
              className="rounded-full border border-line px-7 py-3.5 font-display text-[15px] font-bold text-ink transition-colors hover:border-white/40"
            >
              Leistungen ansehen
            </a>
          </motion.div>
        </div>
      </motion.div>

      {/* scroll cue */}
      <div className="absolute bottom-6 left-1/2 z-10 -translate-x-1/2">
        <div className="flex h-9 w-5 items-start justify-center rounded-full border border-white/25 p-1.5">
          <motion.span
            animate={{ y: [0, 8, 0] }}
            transition={{ duration: 1.8, repeat: Infinity, ease: "easeInOut" }}
            className="h-1.5 w-1.5 rounded-full bg-gold"
          />
        </div>
      </div>
    </section>
  );
}
