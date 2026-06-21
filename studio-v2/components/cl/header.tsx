"use client";

import { useEffect, useState } from "react";
import { motion, useReducedMotion } from "framer-motion";
import { Icon } from "@/components/cl/icons";
import { MAIL } from "@/lib/cl-data";

export function ClHeader() {
  const reduce = useReducedMotion();
  const [show, setShow] = useState(reduce);

  useEffect(() => {
    if (reduce) return;
    const onScroll = () => {
      // reveal once we've scrolled most of the way through the intro
      setShow(window.scrollY > window.innerHeight * 0.85);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, [reduce]);

  return (
    <motion.header
      initial={false}
      animate={{ y: show ? 0 : "-115%", opacity: show ? 1 : 0 }}
      transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
      className="fixed inset-x-0 top-0 z-50 flex items-center justify-between border-b border-line bg-[rgba(7,7,10,0.78)] px-4 py-3 backdrop-blur-[10px] backdrop-saturate-150"
    >
      <a href="#top" className="flex items-center gap-2.5">
        <Icon name="mark" className="h-[26px] w-[26px] text-gold" />
        <span className="font-display text-[15px] font-bold">
          CleanLines <span className="font-semibold text-dim">Studio</span>
        </span>
      </a>
      <a
        href={`mailto:${MAIL}`}
        className="rounded-full bg-gradient-to-br from-gold to-gold-bright px-4 py-2 text-[13px] font-bold text-[#1a1206] transition-transform duration-200 active:scale-95"
      >
        Preview sichern
      </a>
    </motion.header>
  );
}
