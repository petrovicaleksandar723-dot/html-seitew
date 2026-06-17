"use client";

import { motion } from "framer-motion";

/**
 * Scene-transition divider: a gold hairline wipes across from left to right
 * as it enters the viewport, with an optional label that fades up.
 */
export function Divider({ label }: { label?: string }) {
  return (
    <div className="shell content relative z-10 py-2">
      <div className="relative flex items-center gap-5">
        <motion.div
          initial={{ clipPath: "inset(0 100% 0 0)" }}
          whileInView={{ clipPath: "inset(0 0% 0 0)" }}
          viewport={{ once: true, margin: "-20% 0px" }}
          transition={{ duration: 1.1, ease: [0.76, 0, 0.24, 1] }}
          className="h-px flex-1 bg-gradient-to-r from-transparent via-gold/50 to-transparent"
        />
        {label && (
          <motion.span
            initial={{ opacity: 0, y: 8 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-20% 0px" }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="whitespace-nowrap font-mono text-[10px] uppercase tracking-[0.3em] text-muted"
          >
            {label}
          </motion.span>
        )}
        <motion.div
          initial={{ clipPath: "inset(0 0 0 100%)" }}
          whileInView={{ clipPath: "inset(0 0 0 0%)" }}
          viewport={{ once: true, margin: "-20% 0px" }}
          transition={{ duration: 1.1, ease: [0.76, 0, 0.24, 1] }}
          className="h-px flex-1 bg-gradient-to-r from-transparent via-gold/50 to-transparent"
        />
      </div>
    </div>
  );
}
