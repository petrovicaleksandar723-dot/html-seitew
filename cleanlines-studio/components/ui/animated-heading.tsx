"use client";

import { motion, useReducedMotion } from "framer-motion";

export type Token = { t: string; accent?: boolean };
type Line = Token[];

const word = {
  hidden: { y: "115%", opacity: 0 },
  show: {
    y: "0%",
    opacity: 1,
    transition: { duration: 0.85, ease: [0.22, 1, 0.36, 1] as const },
  },
};

/**
 * World-class word-by-word mask reveal. Each word rises from a clipped line.
 * `lines` is an array of lines; each line is tokens, optionally accented
 * (rendered as the serif-italic gold highlight).
 */
export function AnimatedHeading({
  lines,
  className = "",
  as: Tag = "h2",
  startDelay = 0.05,
}: {
  lines: Line[];
  className?: string;
  as?: "h1" | "h2" | "h3";
  startDelay?: number;
}) {
  const reduce = useReducedMotion();
  const container = {
    hidden: {},
    show: {
      transition: { staggerChildren: 0.045, delayChildren: startDelay },
    },
  };

  if (reduce) {
    return (
      <Tag className={className}>
        {lines.map((line, i) => (
          <span key={i} className="block">
            {line.map((tok, j) => (
              <span
                key={j}
                className={
                  tok.accent
                    ? "font-serif font-normal italic text-gradient-gold"
                    : undefined
                }
              >
                {tok.t}{" "}
              </span>
            ))}
          </span>
        ))}
      </Tag>
    );
  }

  return (
    <motion.div
      variants={container}
      initial="hidden"
      whileInView="show"
      viewport={{ once: true, margin: "-10% 0px" }}
    >
      <Tag className={className}>
        {lines.map((line, i) => (
          <span key={i} className="block">
            {line.map((tok, j) =>
              tok.t.split(" ").map((w, k) => (
                <span
                  key={`${j}-${k}`}
                  className="inline-block overflow-hidden align-bottom"
                  style={{ paddingBottom: "0.08em", marginBottom: "-0.08em" }}
                >
                  <motion.span
                    variants={word}
                    className={`inline-block ${
                      tok.accent
                        ? "font-serif font-normal italic text-gradient-gold"
                        : ""
                    }`}
                  >
                    {w}
                    {" "}
                  </motion.span>
                </span>
              ))
            )}
          </span>
        ))}
      </Tag>
    </motion.div>
  );
}
