"use client";

import { useRef } from "react";
import { motion, useReducedMotion } from "framer-motion";
import { Reveal } from "@/components/ui/reveal";
import { REELS } from "@/lib/constants";

function ReelCard({
  n,
  title,
  body,
  index,
}: {
  n: string;
  title: string;
  body: string;
  index: number;
}) {
  const reduce = useReducedMotion();
  const ref = useRef<HTMLDivElement>(null);

  const onMove = (e: React.MouseEvent) => {
    if (reduce || !ref.current) return;
    const r = ref.current.getBoundingClientRect();
    const px = (e.clientX - r.left) / r.width - 0.5;
    const py = (e.clientY - r.top) / r.height - 0.5;
    ref.current.style.transform = `perspective(900px) rotateY(${px * 7}deg) rotateX(${-py * 7}deg) translateY(-4px)`;
  };
  const onLeave = () => {
    if (ref.current) ref.current.style.transform = "";
  };

  return (
    <Reveal delay={index * 0.06}>
      <div
        ref={ref}
        onMouseMove={onMove}
        onMouseLeave={onLeave}
        className="group relative h-full overflow-hidden rounded-2xl border border-line bg-gradient-to-b from-white/[0.04] to-transparent p-7 transition-[transform,border-color] duration-300 ease-out-expo will-change-transform hover:border-gold/30"
      >
        <div className="lightfield -right-16 -top-16 h-44 w-44 bg-gold/0 transition-colors duration-500 group-hover:bg-gold/10" />
        <div className="relative flex aspect-[4/5] flex-col justify-between">
          <div className="flex items-start justify-between">
            <span className="font-mono text-[13px] tracking-[0.2em] text-gold/80">
              {n}
            </span>
            <span className="rounded-full border border-line px-2.5 py-1 font-mono text-[10px] uppercase tracking-[0.15em] text-muted">
              Reel
            </span>
          </div>

          {/* cinematic placeholder frame */}
          <div className="relative my-5 flex-1 overflow-hidden rounded-xl border border-line bg-[radial-gradient(120%_120%_at_30%_20%,rgba(216,178,116,0.16),transparent_60%)]">
            <motion.div
              className="absolute inset-x-6 bottom-6 h-px bg-gradient-to-r from-gold/60 to-transparent"
              animate={reduce ? {} : { opacity: [0.3, 0.9, 0.3] }}
              transition={{ duration: 3, repeat: Infinity, delay: index * 0.4 }}
            />
            <div className="absolute left-1/2 top-1/2 grid h-12 w-12 -translate-x-1/2 -translate-y-1/2 place-items-center rounded-full border border-gold/40 bg-bg/40 backdrop-blur-sm">
              <span className="ml-0.5 h-0 w-0 border-y-[7px] border-l-[11px] border-y-transparent border-l-gold" />
            </div>
          </div>

          <div>
            <h3 className="font-display text-[20px] font-bold tracking-tight">
              {title}
            </h3>
            <p className="mt-2 font-body text-[14px] leading-relaxed text-dim">
              {body}
            </p>
          </div>
        </div>
      </div>
    </Reveal>
  );
}

export function ReelCinema() {
  return (
    <section id="reel-cinema" className="py-[clamp(90px,14vw,170px)]">
      <div className="shell content relative z-10">
        <Reveal>
          <div className="max-w-[680px]">
            <span className="eyebrow">Reel Cinema</span>
            <h2 className="mt-6 font-display text-[clamp(32px,5vw,60px)] font-bold leading-[1.02] tracking-[-0.02em]">
              Content, der nicht wie Werbung wirkt.{" "}
              <span className="font-serif italic font-normal text-gold">
                Sondern wie Marke.
              </span>
            </h2>
            <p className="mt-6 font-body text-[17px] leading-relaxed text-dim">
              Keine zufälligen Posts. Keine langweiligen Videos ohne Richtung.
              Wir entwickeln kurze, starke Content-Formate, die deine Leistung
              hochwertig zeigen und in wenigen Sekunden Interesse auslösen.
            </p>
          </div>
        </Reveal>

        <div className="mt-14 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {REELS.map((r, i) => (
            <ReelCard key={r.n} {...r} index={i} />
          ))}
        </div>
      </div>
    </section>
  );
}
