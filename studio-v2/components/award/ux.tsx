"use client";

import { type ReactNode, useEffect, useRef, useState } from "react";
import {
  motion,
  useReducedMotion,
  useSpring,
  useMotionValue,
  useInView,
  useScroll,
  useTransform,
  animate,
  type MotionProps,
} from "framer-motion";

/* ------------------------------------------------------------------ easing
   Strong custom curves per Emil Kowalski's standards (built-in CSS easings
   are too weak). ease-out for enter/exit, ease-in-out for on-screen movement. */
export const EASE_OUT = [0.23, 1, 0.32, 1] as const; // responsive enter/exit
export const EASE_IN_OUT = [0.77, 0, 0.175, 1] as const; // morph / move on screen
export const EASE_HOVER = [0.4, 0, 0.2, 1] as const; // hover / color
export const SPRING = { type: "spring", stiffness: 260, damping: 30, mass: 0.6 } as const;
export const SPRING_SOFT = { type: "spring", stiffness: 140, damping: 20, mass: 0.7 } as const;

/* ----------------------------------------------------- hover capability gate
   Touch devices fire false :hover on tap — gate decorative hover motion. */
export function useHoverCapable() {
  const [ok, setOk] = useState(false);
  useEffect(() => {
    const mq = window.matchMedia("(hover: hover) and (pointer: fine)");
    const on = () => setOk(mq.matches);
    on();
    mq.addEventListener("change", on);
    return () => mq.removeEventListener("change", on);
  }, []);
  return ok;
}

/* -------------------------------------------------------------------- Reveal
   Subtle, GPU-only (opacity + transform). once. Marketing-length OK (~0.7s). */
export function Reveal({
  children,
  delay = 0,
  y = 18,
  className,
  blur = false,
  once = true,
}: {
  children: ReactNode;
  delay?: number;
  y?: number;
  className?: string;
  blur?: boolean;
  once?: boolean;
}) {
  const reduce = useReducedMotion();
  return (
    <motion.div
      className={className}
      initial={reduce ? { opacity: 0 } : { opacity: 0, y, filter: blur ? "blur(6px)" : undefined }}
      whileInView={{ opacity: 1, y: 0, filter: blur ? "blur(0px)" : undefined }}
      viewport={{ once, margin: "-12% 0px" }}
      transition={{ duration: 0.7, delay, ease: EASE_OUT }}
    >
      {children}
    </motion.div>
  );
}

/* ------------------------------------------------------------ AnimatedHeading
   Each line rises out of a clip mask. ease-out, 30–80ms stagger. */
export function AnimatedHeading({
  lines,
  className,
  delay = 0,
  stagger = 0.07,
  as: Tag = "h2",
}: {
  lines: ReactNode[];
  className?: string;
  delay?: number;
  stagger?: number;
  as?: "h1" | "h2" | "h3";
}) {
  const reduce = useReducedMotion();
  return (
    <Tag className={className}>
      {lines.map((line, i) => (
        <span key={i} className="block overflow-hidden pb-[0.08em]">
          <motion.span
            className="block will-change-transform"
            initial={reduce ? { opacity: 0 } : { y: "115%" }}
            whileInView={reduce ? { opacity: 1 } : { y: "0%" }}
            viewport={{ once: true, margin: "-10% 0px" }}
            transition={{ duration: 0.85, delay: delay + i * stagger, ease: EASE_OUT }}
          >
            {line}
          </motion.span>
        </span>
      ))}
    </Tag>
  );
}

/* ----------------------------------------------------------------- Magnetic
   Decorative mouse-tracking via useSpring (momentum, not raw position).
   Gated to hover-capable pointers. */
export function Magnetic({
  children,
  strength = 0.3,
  className,
}: {
  children: ReactNode;
  strength?: number;
  className?: string;
}) {
  const hover = useHoverCapable();
  const reduce = useReducedMotion();
  const ref = useRef<HTMLDivElement>(null);
  const x = useSpring(0, SPRING);
  const y = useSpring(0, SPRING);

  if (!hover || reduce) return <div className={className}>{children}</div>;

  return (
    <motion.div
      ref={ref}
      style={{ x, y }}
      className={className}
      onPointerMove={(e) => {
        const r = ref.current?.getBoundingClientRect();
        if (!r) return;
        x.set((e.clientX - (r.left + r.width / 2)) * strength);
        y.set((e.clientY - (r.top + r.height / 2)) * strength);
      }}
      onPointerLeave={() => {
        x.set(0);
        y.set(0);
      }}
    >
      {children}
    </motion.div>
  );
}

/* ------------------------------------------------------------------- Button
   Press feedback scale(0.97) @140ms ease-out (asymmetric: press deliberate,
   sheen release fast). */
export function Button({
  href,
  children,
  variant = "primary",
  className = "",
  magnetic = false,
  onClick,
}: {
  href?: string;
  children: ReactNode;
  variant?: "primary" | "ghost" | "dark";
  className?: string;
  magnetic?: boolean;
  onClick?: () => void;
}) {
  const styles =
    variant === "primary"
      ? "bg-gradient-to-br from-gold to-gold-bright text-[#1a1206] shadow-[0_14px_40px_-12px_rgba(216,178,116,0.6)]"
      : variant === "dark"
      ? "border border-gold/40 bg-[#13110c] text-gold-bright"
      : "border border-white/20 bg-white/[0.03] text-ink";

  const Inner = (
    <motion.a
      href={href}
      onClick={onClick}
      whileTap={{ scale: 0.97 }}
      transition={{ duration: 0.14, ease: EASE_OUT }}
      className={`group relative inline-flex cursor-pointer items-center justify-center gap-2 overflow-hidden rounded-full px-7 py-4 text-[15px] font-bold ${styles} ${className}`}
    >
      <span
        aria-hidden
        className="pointer-events-none absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-white/25 to-transparent transition-transform duration-700 ease-out group-hover:translate-x-full"
      />
      <span className="relative z-10 inline-flex items-center gap-2">{children}</span>
    </motion.a>
  );

  return magnetic ? <Magnetic strength={0.25}>{Inner}</Magnetic> : Inner;
}

/* ------------------------------------------------------------------ CountUp */
export function CountUp({
  value,
  suffix = "",
  decimals = 0,
  className,
}: {
  value: number;
  suffix?: string;
  decimals?: number;
  className?: string;
}) {
  const ref = useRef<HTMLSpanElement>(null);
  const inView = useInView(ref, { once: true, margin: "-15% 0px" });
  const mv = useMotionValue(0);
  const [disp, setDisp] = useState((0).toFixed(decimals));
  const reduce = useReducedMotion();
  useEffect(() => {
    if (!inView) return;
    if (reduce) return setDisp(value.toFixed(decimals));
    const c = animate(mv, value, { duration: 1.4, ease: EASE_OUT, onUpdate: (v) => setDisp(v.toFixed(decimals)) });
    return () => c.stop();
  }, [inView, value, decimals, reduce, mv]);
  return (
    <span ref={ref} className={className}>
      {disp}
      {suffix}
    </span>
  );
}

/* --------------------------------------------------------------- LazyVideo */
export function LazyVideo({
  src,
  className,
  eager = false,
}: {
  src: string;
  className?: string;
  eager?: boolean;
}) {
  const ref = useRef<HTMLVideoElement>(null);
  useEffect(() => {
    const v = ref.current;
    if (!v) return;
    if (eager) {
      if (!v.src) v.src = src;
      v.play().catch(() => {});
      return;
    }
    const io = new IntersectionObserver(
      ([e]) => {
        if (e.isIntersecting) {
          if (!v.src) v.src = src;
          v.play().catch(() => {});
        } else v.pause();
      },
      { threshold: 0.3 }
    );
    io.observe(v);
    return () => io.disconnect();
  }, [src, eager]);
  return <video ref={ref} className={className} muted loop playsInline preload="none" />;
}

/* ------------------------------------------------------------------- Phone */
export function Phone({
  children,
  width = 270,
  live = false,
  className = "",
}: {
  children: ReactNode;
  width?: number;
  live?: boolean;
  className?: string;
}) {
  return (
    <div
      className={`relative aspect-[9/19] rounded-[36px] border border-white/[0.16] bg-black p-[7px] shadow-[0_40px_90px_-20px_rgba(0,0,0,0.8),0_0_0_1px_rgba(216,178,116,0.12)] ${className}`}
      style={{ width }}
    >
      <div className="absolute left-1/2 top-[7px] z-[2] h-4 w-[32%] -translate-x-1/2 rounded-b-[12px] bg-black" />
      {live && (
        <span className="absolute right-3.5 top-3.5 z-[3] inline-flex items-center gap-1.5 rounded-full border border-white/25 bg-black/50 px-2.5 py-1 text-[10px] font-extrabold tracking-[0.1em] text-white">
          <span className="h-[7px] w-[7px] rounded-full bg-[#ff5a5a] shadow-[0_0_8px_#ff5a5a]" />
          LIVE
        </span>
      )}
      <div className="relative h-full w-full overflow-hidden rounded-[29px] bg-[#0a0a0c]">{children}</div>
    </div>
  );
}

/* ----------------------------------------------------------------- Marquee
   Predetermined, constant motion → CSS (off main thread), linear, pause on hover. */
export function Marquee({
  children,
  speed = 40,
  className = "",
  reverse = false,
}: {
  children: ReactNode;
  speed?: number;
  className?: string;
  reverse?: boolean;
}) {
  return (
    <div className={`group flex overflow-hidden ${className}`}>
      <div
        className="flex shrink-0 [animation:cl-marquee_linear_infinite] group-hover:[animation-play-state:paused] motion-reduce:[animation-play-state:paused]"
        style={{ animationDuration: `${speed}s`, animationDirection: reverse ? "reverse" : "normal" }}
      >
        <div className="flex shrink-0 items-stretch gap-7 pr-7">{children}</div>
        <div className="flex shrink-0 items-stretch gap-7 pr-7" aria-hidden>
          {children}
        </div>
      </div>
    </div>
  );
}

/* ------------------------------------------------------------ ScrollProgress
   Scroll-linked → no easing (linear), GPU scaleX, origin-left. */
export function ScrollProgress() {
  const { scrollYProgress } = useScroll();
  const scaleX = useSpring(scrollYProgress, { stiffness: 200, damping: 40, mass: 0.4 });
  return (
    <motion.div
      style={{ scaleX }}
      className="fixed inset-x-0 top-0 z-[70] h-[2px] origin-left bg-gradient-to-r from-gold-deep via-gold to-gold-bright"
    />
  );
}

/* ------------------------------------------------------------------ Parallax
   Subtle scroll-linked vertical drift. */
export function Parallax({
  children,
  amount = 60,
  className,
}: {
  children: ReactNode;
  amount?: number;
  className?: string;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const reduce = useReducedMotion();
  const { scrollYProgress } = useScroll({ target: ref, offset: ["start end", "end start"] });
  const y = useTransform(scrollYProgress, [0, 1], [amount, -amount]);
  return (
    <div ref={ref} className={className}>
      <motion.div style={reduce ? undefined : { y }}>{children}</motion.div>
    </div>
  );
}

/* ---------------------------------------------------------------- stagger */
export const stagger = (i: number, base = 0): MotionProps => ({
  initial: { opacity: 0, y: 16 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true, margin: "-8% 0px" },
  transition: { duration: 0.6, delay: base + i * 0.06, ease: EASE_OUT },
});
