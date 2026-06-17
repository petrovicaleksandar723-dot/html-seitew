"use client";

import {
  motion,
  useMotionValue,
  useSpring,
  useReducedMotion,
} from "framer-motion";
import { useRef, type ReactNode } from "react";

type Props = {
  children: ReactNode;
  href?: string;
  variant?: "primary" | "ghost";
  className?: string;
  strength?: number;
  ariaLabel?: string;
};

export function MagneticButton({
  children,
  href = "#kontakt",
  variant = "primary",
  className = "",
  strength = 0.4,
  ariaLabel,
}: Props) {
  const reduce = useReducedMotion();
  const ref = useRef<HTMLAnchorElement>(null);
  const x = useMotionValue(0);
  const y = useMotionValue(0);
  const sx = useSpring(x, { stiffness: 220, damping: 18, mass: 0.4 });
  const sy = useSpring(y, { stiffness: 220, damping: 18, mass: 0.4 });

  const onMove = (e: React.MouseEvent) => {
    if (reduce || !ref.current) return;
    const r = ref.current.getBoundingClientRect();
    x.set((e.clientX - (r.left + r.width / 2)) * strength);
    y.set((e.clientY - (r.top + r.height / 2)) * strength);
  };
  const onLeave = () => {
    x.set(0);
    y.set(0);
  };

  const base =
    "relative inline-flex items-center justify-center gap-2 rounded-full font-display font-bold tracking-tight transition-colors duration-300 will-change-transform";
  const styles =
    variant === "primary"
      ? "bg-gradient-to-br from-gold-bright to-gold-deep text-[#1a1206] shadow-[0_14px_44px_-12px_rgba(216,178,116,0.65)] hover:shadow-[0_20px_56px_-12px_rgba(216,178,116,0.85)] px-8 py-4 text-[15px]"
      : "border border-white/18 text-ink hover:border-white/35 hover:bg-white/[0.04] px-8 py-4 text-[15px] backdrop-blur-sm";

  return (
    <motion.a
      ref={ref}
      href={href}
      aria-label={ariaLabel}
      onMouseMove={onMove}
      onMouseLeave={onLeave}
      style={{ x: sx, y: sy }}
      className={`${base} ${styles} ${className}`}
    >
      {children}
    </motion.a>
  );
}
