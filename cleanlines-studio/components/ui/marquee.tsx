"use client";

import { useRef } from "react";
import {
  motion,
  useScroll,
  useVelocity,
  useTransform,
  useSpring,
  useMotionValue,
  useAnimationFrame,
} from "framer-motion";

const ITEMS = [
  "Reels",
  "KI-Visuals",
  "Captions",
  "Google-Beiträge",
  "Branding",
  "Content-System",
  "Website-Design",
  "Reviews",
];

export function Marquee() {
  const baseX = useMotionValue(0);
  const { scrollY } = useScroll();
  const scrollVelocity = useVelocity(scrollY);
  const smooth = useSpring(scrollVelocity, { damping: 50, stiffness: 400 });
  const factor = useTransform(smooth, [0, 1000], [0, 4], { clamp: false });
  const directional = useRef(1);

  const x = useTransform(baseX, (v) => `${wrap(-50, 0, v)}%`);

  useAnimationFrame((_, delta) => {
    let moveBy = directional.current * 2.4 * (delta / 1000);
    const f = factor.get();
    if (f < 0) directional.current = -1;
    else if (f > 0) directional.current = 1;
    moveBy += directional.current * moveBy * f;
    baseX.set(baseX.get() + moveBy);
  });

  return (
    <section className="border-y border-line py-7">
      <div className="relative flex overflow-hidden">
        <motion.div className="flex whitespace-nowrap" style={{ x }}>
          {[...ITEMS, ...ITEMS, ...ITEMS, ...ITEMS].map((it, i) => (
            <span key={i} className="flex items-center">
              <span className="px-8 font-display text-[clamp(22px,3vw,40px)] font-extrabold tracking-tight text-ink/80">
                {it}
              </span>
              <span className="text-gold">✦</span>
            </span>
          ))}
        </motion.div>
      </div>
    </section>
  );
}

function wrap(min: number, max: number, v: number) {
  const range = max - min;
  const mod = (((v - min) % range) + range) % range;
  return mod + min;
}
