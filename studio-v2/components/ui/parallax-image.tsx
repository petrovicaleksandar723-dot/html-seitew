"use client";

import { useRef } from "react";
import { motion, useReducedMotion, useScroll, useTransform } from "framer-motion";

/**
 * Cinematic parallax image: the picture sits in an over-sized layer that drifts
 * (and optionally scales) as the frame passes through the viewport — the classic
 * "the background moves slower than the page" depth effect, plus a slow Ken-Burns.
 */
export function ParallaxImage({
  src,
  alt,
  className = "",
  amount = 16,
  scale = 1.12,
  priority = false,
  rounded = true,
}: {
  src: string;
  alt: string;
  className?: string;
  amount?: number; // vertical drift in %
  scale?: number; // ken-burns target scale
  priority?: boolean;
  rounded?: boolean;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const reduce = useReducedMotion();
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start end", "end start"],
  });

  const y = useTransform(scrollYProgress, [0, 1], [`-${amount}%`, `${amount}%`]);
  const s = useTransform(scrollYProgress, [0, 0.5, 1], [scale, 1, scale]);

  return (
    <div
      ref={ref}
      className={`relative overflow-hidden ${rounded ? "rounded-[18px]" : ""} ${className}`}
    >
      <motion.img
        src={src}
        alt={alt}
        loading={priority ? "eager" : "lazy"}
        // eslint-disable-next-line @next/next/no-img-element
        style={reduce ? undefined : { y, scale: s }}
        className="absolute inset-0 h-[132%] w-full -translate-y-[16%] object-cover"
      />
      {/* preserve layout height */}
      <div className="invisible">
        <img src={src} alt="" aria-hidden className="w-full" />
      </div>
    </div>
  );
}
