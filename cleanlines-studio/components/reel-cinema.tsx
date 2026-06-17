"use client";

import { useRef, useState } from "react";
import { motion, useReducedMotion } from "framer-motion";
import { Reveal } from "@/components/ui/reveal";
import { REELS } from "@/lib/constants";

const CARD_VIDEOS: Record<number, string> = {
  0: "/videos/reel-1.mp4",
  1: "/videos/reel-2.mp4",
  2: "/videos/reel-3.mp4",
};

/* ---------- Featured showreel ---------- */
function Showreel() {
  const ref = useRef<HTMLVideoElement>(null);
  const [muted, setMuted] = useState(true);

  const toggleSound = () => {
    if (!ref.current) return;
    ref.current.muted = !ref.current.muted;
    setMuted(ref.current.muted);
    if (!ref.current.muted) ref.current.play().catch(() => {});
  };

  return (
    <Reveal>
      <div className="glass group relative mt-14 overflow-hidden rounded-2xl">
        <div className="relative aspect-video w-full">
          <video
            ref={ref}
            className="h-full w-full object-cover"
            src="/videos/showreel.mp4"
            autoPlay
            muted
            loop
            playsInline
            preload="metadata"
          />
          {/* cinematic letterbox grading */}
          <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(120%_120%_at_50%_50%,transparent_55%,rgba(5,5,5,0.55)_100%)]" />
          <div className="pointer-events-none absolute inset-x-0 bottom-0 h-28 bg-gradient-to-t from-bg/90 to-transparent" />

          <div className="absolute bottom-5 left-6 flex items-center gap-3">
            <span className="flex h-2 w-2 items-center justify-center">
              <span className="absolute h-2 w-2 animate-ping rounded-full bg-gold/70" />
              <span className="h-2 w-2 rounded-full bg-gold" />
            </span>
            <span className="font-mono text-[11px] uppercase tracking-[0.25em] text-ink/90">
              Showreel · Cleanlines Studios
            </span>
          </div>

          <button
            onClick={toggleSound}
            aria-label={muted ? "Ton an" : "Ton aus"}
            className="absolute bottom-4 right-4 grid h-11 w-11 place-items-center rounded-full border border-white/20 bg-bg/40 text-ink backdrop-blur-md transition-colors hover:border-gold/50 hover:text-gold"
          >
            {muted ? (
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                <path d="M11 5 6 9H3v6h3l5 4V5Z" fill="currentColor" />
                <path d="m17 9 4 6M21 9l-4 6" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
              </svg>
            ) : (
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                <path d="M11 5 6 9H3v6h3l5 4V5Z" fill="currentColor" />
                <path d="M16 8a5 5 0 0 1 0 8M18.5 5.5a9 9 0 0 1 0 13" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
              </svg>
            )}
          </button>
        </div>
      </div>
    </Reveal>
  );
}

/* ---------- Reel card (with optional looping clip) ---------- */
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
  const video = CARD_VIDEOS[index];

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

          {/* media frame */}
          <div className="relative my-5 flex-1 overflow-hidden rounded-xl border border-line bg-[radial-gradient(120%_120%_at_30%_20%,rgba(216,178,116,0.16),transparent_60%)]">
            {video ? (
              <video
                className="absolute inset-0 h-full w-full object-cover opacity-90 transition-opacity duration-500 group-hover:opacity-100"
                src={video}
                autoPlay
                muted
                loop
                playsInline
                preload="metadata"
              />
            ) : (
              <>
                <motion.div
                  className="absolute inset-x-6 bottom-6 h-px bg-gradient-to-r from-gold/60 to-transparent"
                  animate={reduce ? {} : { opacity: [0.3, 0.9, 0.3] }}
                  transition={{ duration: 3, repeat: Infinity, delay: index * 0.4 }}
                />
                <div className="absolute left-1/2 top-1/2 grid h-12 w-12 -translate-x-1/2 -translate-y-1/2 place-items-center rounded-full border border-gold/40 bg-bg/40 backdrop-blur-sm">
                  <span className="ml-0.5 h-0 w-0 border-y-[7px] border-l-[11px] border-y-transparent border-l-gold" />
                </div>
              </>
            )}
            <div className="pointer-events-none absolute inset-0 bg-gradient-to-t from-bg/40 to-transparent" />
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

        <Showreel />

        <div className="mt-5 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {REELS.map((r, i) => (
            <ReelCard key={r.n} {...r} index={i} />
          ))}
        </div>
      </div>
    </section>
  );
}
