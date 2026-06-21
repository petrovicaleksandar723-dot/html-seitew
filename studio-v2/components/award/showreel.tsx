"use client";

import { useEffect, useRef, useState } from "react";
import { motion, useReducedMotion, useScroll, useSpring, useTransform } from "framer-motion";
import { AnimatedHeading, LazyVideo, Phone, Reveal } from "@/components/award/ux";
import { SHOWREEL } from "@/lib/cl-data";

export function AwShowreel() {
  const reduce = useReducedMotion();
  const [mobile, setMobile] = useState(false);

  useEffect(() => {
    const mq = window.matchMedia("(max-width: 1023px)");
    const on = () => setMobile(mq.matches);
    on();
    mq.addEventListener("change", on);
    return () => mq.removeEventListener("change", on);
  }, []);

  const ref = useRef<HTMLDivElement>(null);
  const track = useRef<HTMLDivElement>(null);
  const [distance, setDistance] = useState(0);

  useEffect(() => {
    const measure = () => {
      if (!track.current) return;
      setDistance(Math.max(0, track.current.scrollWidth - window.innerWidth + 160));
    };
    measure();
    window.addEventListener("resize", measure);
    return () => window.removeEventListener("resize", measure);
  }, [mobile, reduce]);

  const { scrollYProgress } = useScroll({ target: ref, offset: ["start start", "end end"] });
  const xRaw = useTransform(scrollYProgress, [0, 1], [0, -distance]);
  const x = useSpring(xRaw, { stiffness: 120, damping: 30, mass: 0.5 });

  const Header = (
    <div className="mx-auto max-w-[1320px] px-5 sm:px-8">
      <span className="font-mono text-[12px] uppercase tracking-[0.2em] text-gold">Showreel</span>
      <div className="flex flex-wrap items-end justify-between gap-x-8 gap-y-4">
        <AnimatedHeading
          as="h2"
          lines={["So sieht dein", <span key="g" className="text-gold">Content aus.</span>]}
          className="mt-5 font-display text-[clamp(34px,5.5vw,68px)] font-extrabold leading-[1.02] tracking-[-0.03em]"
        />
        <span className="hidden font-mono text-[12px] uppercase tracking-[0.2em] text-muted lg:inline-flex lg:items-center lg:gap-2">
          scroll <span aria-hidden className="text-gold">&rarr;</span>
        </span>
      </div>
      <Reveal className="mt-5 max-w-[560px] text-dim">
        Echte Beispiele aus unseren Reel-Produktionen &ndash; fertig f&uuml;r Instagram, TikTok &amp; Co.
      </Reveal>
    </div>
  );

  if (reduce || mobile) {
    return (
      <section className="py-24">
        {Header}
        <div className="no-bar mt-12 flex gap-6 overflow-x-auto px-5 pb-4 [scroll-snap-type:x_mandatory]">
          {SHOWREEL.map((s, i) => (
            <div key={i} className="flex-none [scroll-snap-align:center]">
              <Phone width={210} live={i === 0}>
                <LazyVideo src={s.src} className="h-full w-full object-cover" />
              </Phone>
              <div className="mt-3 flex items-center gap-2 font-mono text-[11px] uppercase tracking-[0.18em] text-muted">
                <span className="text-gold">/0{i + 1}</span> {s.cap}
              </div>
            </div>
          ))}
        </div>
      </section>
    );
  }

  return (
    <section className="pt-24">
      {Header}
      <div ref={ref} style={{ height: `${distance + 1200}px` }} className="relative">
        <div className="sticky top-0 flex h-screen items-center overflow-hidden">
          <motion.div
            ref={track}
            style={{ x }}
            className="flex gap-8 pl-[max(24px,calc((100vw-1320px)/2))] pr-32 will-change-transform"
          >
            {SHOWREEL.map((s, i) => (
              <div key={i} className="flex-none">
                <div className="mb-3 flex items-center gap-2 font-mono text-[11px] uppercase tracking-[0.18em] text-muted">
                  <span className="text-gold">/0{i + 1}</span> {s.cap}
                </div>
                <Phone width={260} live={i === 0}>
                  <LazyVideo src={s.src} className="h-full w-full object-cover" />
                </Phone>
              </div>
            ))}
          </motion.div>
        </div>
      </div>
    </section>
  );
}
