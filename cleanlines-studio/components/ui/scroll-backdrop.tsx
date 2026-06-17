"use client";

import { motion, useScroll, useTransform, useSpring } from "framer-motion";

/**
 * Fixed atmospheric layer behind all content. Two warm light fields drift and
 * shift opacity as you scroll, so the whole page subtly changes tone scene to
 * scene — the "color shift" between sections.
 */
export function ScrollBackdrop() {
  const { scrollYProgress } = useScroll();
  const p = useSpring(scrollYProgress, { stiffness: 80, damping: 30 });

  const y1 = useTransform(p, [0, 1], ["8%", "78%"]);
  const x1 = useTransform(p, [0, 0.5, 1], ["12%", "60%", "20%"]);
  const o1 = useTransform(p, [0, 0.5, 1], [0.12, 0.06, 0.14]);

  const y2 = useTransform(p, [0, 1], ["88%", "18%"]);
  const x2 = useTransform(p, [0, 0.5, 1], ["80%", "30%", "70%"]);
  const o2 = useTransform(p, [0, 0.5, 1], [0.08, 0.13, 0.07]);

  return (
    <div className="pointer-events-none fixed inset-0 -z-10 overflow-hidden bg-bg">
      <motion.div
        className="absolute h-[55vw] w-[55vw] rounded-full"
        style={{
          top: y1,
          left: x1,
          opacity: o1,
          x: "-50%",
          y: "-50%",
          filter: "blur(110px)",
          background:
            "radial-gradient(circle, rgba(216,178,116,0.9), transparent 65%)",
        }}
      />
      <motion.div
        className="absolute h-[48vw] w-[48vw] rounded-full"
        style={{
          top: y2,
          left: x2,
          opacity: o2,
          x: "-50%",
          y: "-50%",
          filter: "blur(120px)",
          background:
            "radial-gradient(circle, rgba(168,127,62,0.9), transparent 65%)",
        }}
      />
    </div>
  );
}
