"use client";

import {
  type ReactNode,
  useEffect,
  useRef,
  useState,
} from "react";
import {
  motion,
  useReducedMotion,
  useSpring,
  useMotionValue,
  useInView,
  animate,
  type MotionProps,
} from "framer-motion";

export const EASE = [0.16, 1, 0.3, 1] as const;

/* ------------------------------------------------------------------ Reveal */
export function Reveal({
  children,
  delay = 0,
  y = 24,
  className,
  blur = true,
}: {
  children: ReactNode;
  delay?: number;
  y?: number;
  className?: string;
  blur?: boolean;
}) {
  const reduce = useReducedMotion();
  return (
    <motion.div
      className={className}
      initial={reduce ? false : { opacity: 0, y, filter: blur ? "blur(8px)" : "blur(0px)" }}
      whileInView={{ opacity: 1, y: 0, filter: "blur(0px)" }}
      viewport={{ once: true, margin: "-10% 0px" }}
      transition={{ duration: 0.85, delay, ease: EASE }}
    >
      {children}
    </motion.div>
  );
}

/* --------------------------------------------------------- AnimatedHeading */
/** Each line rises out of a clip mask with a stagger. Pass lines as nodes;
 *  wrap gold words in <span className="text-gold"> inside a line. */
export function AnimatedHeading({
  lines,
  className,
  delay = 0,
  as: Tag = "h2",
}: {
  lines: ReactNode[];
  className?: string;
  delay?: number;
  as?: "h1" | "h2" | "h3";
}) {
  const reduce = useReducedMotion();
  return (
    <Tag className={className}>
      {lines.map((line, i) => (
        <span key={i} className="block overflow-hidden pb-[0.05em]">
          <motion.span
            className="block will-change-transform"
            initial={reduce ? false : { y: "115%" }}
            whileInView={{ y: "0%" }}
            viewport={{ once: true, margin: "-8% 0px" }}
            transition={{ duration: 0.9, delay: delay + i * 0.09, ease: EASE }}
          >
            {line}
          </motion.span>
        </span>
      ))}
    </Tag>
  );
}

/* -------------------------------------------------------------- Eyebrow */
export function Eyebrow({
  children,
  dark = false,
  className = "",
}: {
  children: ReactNode;
  dark?: boolean;
  className?: string;
}) {
  const reduce = useReducedMotion();
  return (
    <motion.span
      initial={reduce ? false : { opacity: 0, y: 10 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-10% 0px" }}
      transition={{ duration: 0.6, ease: EASE }}
      className={`inline-flex items-center gap-2 rounded-full border px-3.5 py-1.5 font-mono text-[11px] font-bold uppercase tracking-[0.16em] ${
        dark
          ? "border-[rgba(138,109,46,0.4)] bg-[rgba(138,109,46,0.08)] text-[#8a6d2e]"
          : "border-gold/30 bg-gold/[0.07] text-gold"
      } ${className}`}
    >
      <span className="relative flex h-1.5 w-1.5">
        <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-current opacity-60" />
        <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-current" />
      </span>
      {children}
    </motion.span>
  );
}

/* -------------------------------------------------------------- Magnetic */
export function Magnetic({
  children,
  strength = 0.35,
  className,
}: {
  children: ReactNode;
  strength?: number;
  className?: string;
}) {
  const reduce = useReducedMotion();
  const ref = useRef<HTMLDivElement>(null);
  const x = useSpring(0, { stiffness: 200, damping: 16, mass: 0.5 });
  const y = useSpring(0, { stiffness: 200, damping: 16, mass: 0.5 });

  if (reduce) return <div className={className}>{children}</div>;

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

/* --------------------------------------------------------------- Buttons */
type BtnProps = {
  href: string;
  children: ReactNode;
  variant?: "primary" | "ghost" | "dark";
  className?: string;
  magnetic?: boolean;
};

export function Button({ href, children, variant = "primary", className = "", magnetic = false }: BtnProps) {
  const base =
    "group relative inline-flex items-center justify-center gap-2 overflow-hidden rounded-[14px] px-6 py-4 text-center text-[15.5px] font-bold transition-transform duration-300 ease-out-expo active:scale-[0.97]";
  const styles =
    variant === "primary"
      ? "bg-gradient-to-br from-gold to-gold-bright text-[#1a1206] shadow-[0_14px_34px_-10px_rgba(216,178,116,0.55)]"
      : variant === "dark"
      ? "border border-gold/40 bg-[#13110c] text-gold-bright"
      : "border border-white/20 bg-white/[0.03] text-ink hover:border-white/40";

  const inner = (
    <a href={href} className={`${base} ${styles} ${className}`}>
      {/* sheen sweep on hover */}
      <span
        aria-hidden
        className="pointer-events-none absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-white/25 to-transparent transition-transform duration-700 ease-out-expo group-hover:translate-x-full"
      />
      <span className="relative z-10 inline-flex items-center gap-2">{children}</span>
    </a>
  );

  return magnetic ? <Magnetic strength={0.25}>{inner}</Magnetic> : inner;
}

/* --------------------------------------------------------------- CountUp */
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
    if (reduce) {
      setDisp(value.toFixed(decimals));
      return;
    }
    const controls = animate(mv, value, {
      duration: 1.5,
      ease: EASE,
      onUpdate: (v) => setDisp(v.toFixed(decimals)),
    });
    return () => controls.stop();
  }, [inView, value, decimals, reduce, mv]);

  return (
    <span ref={ref} className={className}>
      {disp}
      {suffix}
    </span>
  );
}

/* ------------------------------------------------------------- LazyVideo */
export function LazyVideo({
  src,
  className,
  eager = false,
  poster,
}: {
  src: string;
  className?: string;
  eager?: boolean;
  poster?: string;
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
        } else {
          v.pause();
        }
      },
      { threshold: 0.35 }
    );
    io.observe(v);
    return () => io.disconnect();
  }, [src, eager]);

  return (
    <video
      ref={ref}
      className={className}
      muted
      loop
      playsInline
      preload="none"
      poster={poster}
    />
  );
}

/* ----------------------------------------------------------------- Phone */
export function Phone({
  children,
  width = 270,
  live = false,
  className = "",
  style,
}: {
  children: ReactNode;
  width?: number;
  live?: boolean;
  className?: string;
  style?: React.CSSProperties;
}) {
  return (
    <div
      className={`relative aspect-[9/19] rounded-[34px] border border-white/[0.16] bg-black p-[7px] shadow-[0_30px_70px_rgba(0,0,0,0.65),0_0_0_1px_rgba(216,178,116,0.12)] ${className}`}
      style={{ width, ...style }}
    >
      <div className="absolute left-1/2 top-[7px] z-[2] h-4 w-[32%] -translate-x-1/2 rounded-b-[12px] bg-black" />
      {live && (
        <span className="absolute right-3.5 top-3.5 z-[3] inline-flex items-center gap-1.5 rounded-full border border-white/25 bg-black/50 px-2.5 py-1 text-[10.5px] font-extrabold tracking-[0.1em] text-white">
          <span className="h-[7px] w-[7px] animate-pulse rounded-full bg-[#ff5a5a] shadow-[0_0_8px_#ff5a5a]" />
          LIVE
        </span>
      )}
      <div className="relative h-full w-full overflow-hidden rounded-[27px] bg-[#0a0a0c]">
        {children}
      </div>
    </div>
  );
}

/* ----------------------------------------------------------------- Stagger */
export const stagger = (i: number, base = 0) => ({
  initial: { opacity: 0, y: 22 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true, margin: "-8% 0px" },
  transition: { duration: 0.7, delay: base + i * 0.07, ease: EASE },
}) satisfies MotionProps;
