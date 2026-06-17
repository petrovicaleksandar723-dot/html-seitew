"use client";

import { useEffect, useRef, useState } from "react";
import {
  motion,
  useReducedMotion,
  useScroll,
  useTransform,
  useSpring,
} from "framer-motion";
import { Reveal } from "@/components/ui/reveal";
import { AnimatedHeading } from "@/components/ui/animated-heading";
import { REELS } from "@/lib/constants";
import { asset } from "@/lib/asset";

const CARD_VIDEOS: Record<number, string> = {
  0: asset("/videos/reel-1.mp4"),
  1: asset("/videos/reel-2.mp4"),
  2: asset("/videos/reel-3.mp4"),
};

/* ---------- Featured showreel (scroll-scaled) ---------- */
function Showreel() {
  const wrap = useRef<HTMLDivElement>(null);
  const vid = useRef<HTMLVideoElement>(null);
  const [muted, setMuted] = useState(true);
  const { scrollYProgress } = useScroll({
    target: wrap,
    offset: ["start 90%", "start 30%"],
  });
  const scale = useTransform(scrollYProgress, [0, 1], [0.9, 1]);
  const opacity = useTransform(scrollYProgress, [0, 1], [0.4, 1]);

  const toggle = () => {
    if (!vid.current) return;
    vid.current.muted = !vid.current.muted;
    setMuted(vid.current.muted);
    if (!vid.current.muted) vid.current.play().catch(() => {});
  };

  return (
    <Reveal>
      <motion.div
        ref={wrap}
        style={{ scale, opacity }}
        className="glass group relative mt-12 overflow-hidden rounded-2xl"
      >
        <div className="relative aspect-video w-full">
          <video
            ref={vid}
            className="h-full w-full object-cover"
            src={asset("/videos/showreel.mp4")}
            autoPlay
            muted
            loop
            playsInline
            preload="metadata"
          />
          <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(120%_120%_at_50%_50%,transparent_55%,rgba(5,5,5,0.55)_100%)]" />
          <div className="pointer-events-none absolute inset-x-0 bottom-0 h-28 bg-gradient-to-t from-bg/90 to-transparent" />
          <div className="absolute bottom-5 left-6 flex items-center gap-3">
            <span className="relative flex h-2 w-2 items-center justify-center">
              <span className="absolute h-2 w-2 animate-ping rounded-full bg-gold/70" />
              <span className="h-2 w-2 rounded-full bg-gold" />
            </span>
            <span className="font-mono text-[11px] uppercase tracking-[0.25em] text-ink/90">
              Showreel · Cleanlines Studios
            </span>
          </div>
          <button
            onClick={toggle}
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
      </motion.div>
    </Reveal>
  );
}

/* ---------- Card ---------- */
function ReelCard({ n, title, body, index }: { n: string; title: string; body: string; index: number }) {
  const reduce = useReducedMotion();
  const video = CARD_VIDEOS[index];
  const card = useRef<HTMLDivElement>(null);
  const vid = useRef<HTMLVideoElement>(null);
  const [sound, setSound] = useState(false);

  const onMove = (e: React.MouseEvent) => {
    if (reduce || !card.current) return;
    const r = card.current.getBoundingClientRect();
    const px = (e.clientX - r.left) / r.width - 0.5;
    const py = (e.clientY - r.top) / r.height - 0.5;
    card.current.style.transform = `perspective(1100px) rotateY(${px * 7}deg) rotateX(${-py * 7}deg) translate3d(${px * 12}px, ${py * 12}px, 0) scale(1.02)`;
  };
  const onEnter = () => {
    if (vid.current) {
      vid.current.muted = false;
      vid.current.play().catch(() => {});
      setSound(true);
    }
  };
  const onLeave = () => {
    if (card.current) card.current.style.transform = "";
    if (vid.current) {
      vid.current.muted = true;
      setSound(false);
    }
  };

  return (
    <div
      ref={card}
      data-hot
      onMouseMove={onMove}
      onMouseEnter={onEnter}
      onMouseLeave={onLeave}
      className="group relative h-[68vh] max-h-[620px] w-[84vw] flex-none overflow-hidden rounded-2xl border border-line bg-gradient-to-b from-white/[0.04] to-transparent p-7 transition-[border-color] duration-300 ease-out-expo will-change-transform hover:border-gold/40 sm:w-[440px]"
    >
      <div className="relative flex h-full flex-col justify-between">
        <div className="flex items-start justify-between">
          <span className="font-mono text-[13px] tracking-[0.2em] text-gold/80">{n}</span>
          <span className="flex items-center gap-2">
            {video && (
              <span className="flex items-center gap-1.5 rounded-full border border-line px-2.5 py-1 font-mono text-[10px] uppercase tracking-[0.12em] text-muted transition-colors group-hover:border-gold/40 group-hover:text-gold">
                {sound ? (
                  <svg width="11" height="11" viewBox="0 0 24 24" fill="none">
                    <path d="M11 5 6 9H3v6h3l5 4V5Z" fill="currentColor" />
                    <path d="M16 8a5 5 0 0 1 0 8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                  </svg>
                ) : (
                  <svg width="11" height="11" viewBox="0 0 24 24" fill="none">
                    <path d="M11 5 6 9H3v6h3l5 4V5Z" fill="currentColor" />
                    <path d="m17 9 4 6M21 9l-4 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                  </svg>
                )}
                {sound ? "Ton" : "Hover"}
              </span>
            )}
            <span className="rounded-full border border-line px-2.5 py-1 font-mono text-[10px] uppercase tracking-[0.15em] text-muted">
              Reel
            </span>
          </span>
        </div>
        <div className="relative my-5 flex-1 overflow-hidden rounded-xl border border-line bg-[radial-gradient(120%_120%_at_30%_20%,rgba(216,178,116,0.16),transparent_60%)]">
          {video ? (
            <video
              ref={vid}
              className="absolute inset-0 h-full w-full object-cover opacity-90 transition-opacity duration-500 group-hover:opacity-100"
              src={video}
              autoPlay
              muted
              loop
              playsInline
              preload="metadata"
            />
          ) : (
            <div className="absolute left-1/2 top-1/2 grid h-12 w-12 -translate-x-1/2 -translate-y-1/2 place-items-center rounded-full border border-gold/40 bg-bg/40 backdrop-blur-sm">
              <span className="ml-0.5 h-0 w-0 border-y-[7px] border-l-[11px] border-y-transparent border-l-gold" />
            </div>
          )}
          <div className="pointer-events-none absolute inset-0 bg-gradient-to-t from-bg/50 to-transparent" />
        </div>
        <div>
          <h3 className="font-display text-[22px] font-bold tracking-tight">{title}</h3>
          <p className="mt-2 font-body text-[14px] leading-relaxed text-dim">{body}</p>
        </div>
      </div>
    </div>
  );
}

/* ---------- Pinned horizontal gallery ---------- */
function HorizontalReels() {
  const reduce = useReducedMotion();
  const section = useRef<HTMLDivElement>(null);
  const track = useRef<HTMLDivElement>(null);
  const [distance, setDistance] = useState(0);
  // Default desktop; pinned translateX is janky on touch, so small screens
  // fall back to the simple scroll row just like reduced-motion users.
  const [mobile, setMobile] = useState(false);

  useEffect(() => {
    const mq = window.matchMedia("(max-width: 1023px)");
    const onMq = () => setMobile(mq.matches);
    onMq();
    mq.addEventListener("change", onMq);
    return () => mq.removeEventListener("change", onMq);
  }, []);

  useEffect(() => {
    const measure = () => {
      if (!track.current) return;
      setDistance(Math.max(0, track.current.scrollWidth - window.innerWidth + 80));
    };
    measure();
    // re-measure after layout / fonts / video metadata settle
    const t1 = setTimeout(measure, 300);
    const t2 = setTimeout(measure, 1200);
    window.addEventListener("resize", measure);
    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
      window.removeEventListener("resize", measure);
    };
  }, []);

  const { scrollYProgress } = useScroll({
    target: section,
    offset: ["start start", "end end"],
  });
  const xRaw = useTransform(scrollYProgress, [0, 1], [0, -distance]);
  const x = useSpring(xRaw, { stiffness: 120, damping: 30, mass: 0.5 });

  if (reduce || mobile) {
    return (
      <div className="shell content no-bar mt-10 flex gap-5 overflow-x-auto pb-4">
        {REELS.map((r, i) => (
          <ReelCard key={r.n} {...r} index={i} />
        ))}
      </div>
    );
  }

  return (
    <div
      ref={section}
      style={{ height: `${Math.max(distance, 1) + 800}px` }}
      className="relative mt-10"
    >
      <div className="sticky top-0 flex h-screen items-center overflow-hidden">
        <motion.div ref={track} style={{ x }} className="flex gap-5 pl-[max(24px,calc((100vw-1240px)/2))] pr-20">
          {REELS.map((r, i) => (
            <ReelCard key={r.n} {...r} index={i} />
          ))}
          <div className="flex w-[40vw] flex-none items-center sm:w-[280px]">
            <div className="font-display text-[clamp(28px,4vw,46px)] font-extrabold leading-tight tracking-tight text-ink/30">
              Dein Format
              <br />
              fehlt hier?
              <br />
              <span className="text-gold/70">Reden wir.</span>
            </div>
          </div>
        </motion.div>
        {/* edge fades so partially-visible cards look intentional, not cut off */}
        <div className="pointer-events-none absolute inset-y-0 right-0 z-10 w-24 bg-gradient-to-l from-bg to-transparent" />
        <div className="pointer-events-none absolute inset-y-0 left-0 z-10 w-16 bg-gradient-to-r from-bg to-transparent" />
      </div>
    </div>
  );
}

export function ReelCinema() {
  const sectionRef = useRef<HTMLElement>(null);
  // pause this section's clips when it's off-screen (frees video decoders)
  useEffect(() => {
    const el = sectionRef.current;
    if (!el) return;
    const io = new IntersectionObserver(
      ([entry]) => {
        el.querySelectorAll("video").forEach((v) => {
          if (entry.isIntersecting) (v as HTMLVideoElement).play().catch(() => {});
          else (v as HTMLVideoElement).pause();
        });
      },
      { rootMargin: "250px" }
    );
    io.observe(el);
    return () => io.disconnect();
  }, []);

  return (
    <section ref={sectionRef} id="reel-cinema" className="py-[clamp(90px,14vw,170px)]">
      <div className="shell content relative z-10">
        <Reveal>
          <span className="eyebrow">Reel Cinema</span>
        </Reveal>
        <AnimatedHeading
          className="mt-6 max-w-[760px] font-display text-[clamp(32px,5vw,60px)] font-bold leading-[1.02] tracking-[-0.02em]"
          lines={[
            [{ t: "Content, der nicht wie Werbung wirkt." }],
            [{ t: "Sondern wie Marke.", accent: true }],
          ]}
        />
        <Reveal delay={0.1}>
          <p className="mt-6 max-w-[640px] font-body text-[17px] leading-relaxed text-dim">
            Keine zufälligen Posts. Keine langweiligen Videos ohne Richtung. Wir
            entwickeln kurze, starke Content-Formate, die deine Leistung
            hochwertig zeigen und in wenigen Sekunden Interesse auslösen.
          </p>
        </Reveal>
        <Showreel />
      </div>

      <HorizontalReels />
    </section>
  );
}
