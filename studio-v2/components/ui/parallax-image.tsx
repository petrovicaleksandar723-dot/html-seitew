"use client";

import { useRef } from "react";
import { motion, useReducedMotion, useScroll, useTransform } from "framer-motion";

/**
 * Cinematic parallax image. The frame is a fixed-aspect, overflow-hidden box
 * (the caller passes the aspect via className, e.g. `aspect-[4/5]`). Inside, an
 * over-scanned, centered image drifts vertically as the frame crosses the
 * viewport — depth without ever exposing an edge and without aggressive zoom.
 */
export function ParallaxImage({
  src,
  alt,
  className = "",
  amount = 10,
  priority = false,
  rounded = true,
}: {
  src: string;
  alt: string;
  className?: string;
  amount?: number; // vertical drift, % of frame height
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

  return (
    <div
      ref={ref}
      className={`relative overflow-hidden bg-surface ${rounded ? "rounded-[18px]" : ""} ${className}`}
    >
      <motion.img
        src={src}
        alt={alt}
        loading={priority ? "eager" : "lazy"}
        style={reduce ? undefined : { y }}
        className="absolute left-1/2 top-1/2 h-[124%] w-[124%] max-w-none -translate-x-1/2 -translate-y-1/2 object-cover will-change-transform"
      />
    </div>
  );
}
