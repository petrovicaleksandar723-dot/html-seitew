"use client";

import { motion, useReducedMotion } from "framer-motion";

export type Token = { t: string; accent?: boolean };
type Line = Token[];

/**
 * Hero-grade headline: every character rises + de-blurs in sequence, then a
 * soft gold light streak sweeps across the whole headline on a loop.
 */
export function CharHeading({
  lines,
  className = "",
  startDelay = 0.05,
  as: Tag = "h1",
}: {
  lines: Line[];
  className?: string;
  startDelay?: number;
  as?: "h1" | "h2";
}) {
  const reduce = useReducedMotion();

  const container = {
    hidden: {},
    show: {
      transition: { staggerChildren: 0.022, delayChildren: startDelay },
    },
  };
  const char = {
    hidden: { opacity: 0, y: "0.5em", filter: "blur(8px)" },
    show: {
      opacity: 1,
      y: "0em",
      filter: "blur(0px)",
      transition: { duration: 0.6, ease: [0.22, 1, 0.36, 1] as const },
    },
  };

  const renderToken = (tok: Token, key: string) => {
    const words = tok.t.split(" ");
    return words.map((w, wi) => (
      <span
        key={`${key}-${wi}`}
        className={`inline-block whitespace-nowrap ${
          tok.accent ? "font-serif font-normal italic text-gradient-gold" : ""
        }`}
      >
        {w.split("").map((c, ci) =>
          reduce ? (
            <span key={ci} className="inline-block">
              {c}
            </span>
          ) : (
            <motion.span key={ci} variants={char} className="inline-block">
              {c}
            </motion.span>
          )
        )}
        {wi < words.length - 1 ? " " : null}
      </span>
    ));
  };

  return (
    <motion.div
      className="relative"
      variants={reduce ? undefined : container}
      initial={reduce ? undefined : "hidden"}
      whileInView={reduce ? undefined : "show"}
      viewport={{ once: true, margin: "-8% 0px" }}
    >
      <Tag className={className}>
        {lines.map((line, i) => (
          <span key={i} className="block">
            {line.map((tok, j) => renderToken(tok, `${i}-${j} `))}{" "}
          </span>
        ))}
      </Tag>

      {/* gold light sweep */}
      {!reduce && (
        <motion.span
          aria-hidden
          className="pointer-events-none absolute inset-0 z-10"
          style={{ mixBlendMode: "screen" }}
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
        >
          <motion.span
            className="absolute inset-y-0 -left-1/3 w-1/3"
            style={{
              background:
                "linear-gradient(105deg, transparent, rgba(244,215,158,0.45), transparent)",
              filter: "blur(6px)",
            }}
            animate={{ x: ["0%", "440%"] }}
            transition={{
              duration: 1.6,
              ease: "easeInOut",
              repeat: Infinity,
              repeatDelay: 3.5,
              delay: startDelay + 1.1,
            }}
          />
        </motion.span>
      )}
    </motion.div>
  );
}
