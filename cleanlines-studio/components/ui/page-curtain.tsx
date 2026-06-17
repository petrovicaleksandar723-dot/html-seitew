"use client";

import { useEffect, useRef } from "react";
import { motion, useAnimationControls } from "framer-motion";
import { lenisRef } from "@/lib/lenis";
import { LogoMark } from "@/components/ui/logo";

const variants = {
  hidden: { y: "100%" },
  cover: { y: "0%" },
  reveal: { y: "-100%" },
};

const ease = [0.76, 0, 0.24, 1] as const;

/**
 * Gold curtain that wipes up over the viewport during in-page anchor jumps,
 * scrolls underneath, then lifts away — a cinematic scene change.
 */
export function PageCurtain() {
  const controls = useAnimationControls();
  const busy = useRef(false);

  useEffect(() => {
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    const onClick = async (e: MouseEvent) => {
      const a = (e.target as HTMLElement)?.closest(
        'a[href^="#"]'
      ) as HTMLAnchorElement | null;
      if (!a) return;
      const id = a.getAttribute("href");
      if (!id || id === "#") return;
      const el = document.querySelector(id) as HTMLElement | null;
      if (!el) return;

      e.preventDefault();

      const scroll = () => {
        if (lenisRef.current) lenisRef.current.scrollTo(el, { immediate: true });
        else el.scrollIntoView();
      };

      if (reduce) {
        scroll();
        return;
      }
      if (busy.current) return;
      busy.current = true;

      await controls.start("cover", { duration: 0.5, ease });
      scroll();
      await new Promise((r) => setTimeout(r, 90));
      await controls.start("reveal", { duration: 0.6, ease });
      controls.set("hidden");
      busy.current = false;
    };

    document.addEventListener("click", onClick);
    return () => document.removeEventListener("click", onClick);
  }, [controls]);

  return (
    <motion.div
      aria-hidden
      variants={variants}
      initial="hidden"
      animate={controls}
      className="pointer-events-none fixed inset-0 z-[120] flex items-center justify-center"
      style={{
        background:
          "linear-gradient(180deg, #0a0806 0%, #1a1308 55%, #0a0806 100%)",
      }}
    >
      <div className="lightfield h-[40vh] w-[40vh] bg-gold/15" />
      <LogoMark className="h-16 w-16 drop-shadow-[0_2px_24px_rgba(216,178,116,0.6)]" />
    </motion.div>
  );
}
