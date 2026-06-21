"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence, useReducedMotion } from "framer-motion";
import { Icon } from "@/components/cl/icons";
import { Button, EASE_OUT } from "@/components/award/ux";
import { MAIL } from "@/lib/cl-data";

const LINKS = [
  { href: "#leistungen", label: "Leistungen" },
  { href: "#branchen", label: "Branchen" },
  { href: "#pakete", label: "Pakete" },
  { href: "#faq", label: "FAQ" },
];

export function AwardNav() {
  const reduce = useReducedMotion();
  const [solid, setSolid] = useState(false);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const on = () => setSolid(window.scrollY > 40);
    on();
    window.addEventListener("scroll", on, { passive: true });
    return () => window.removeEventListener("scroll", on);
  }, []);

  return (
    <motion.header
      initial={reduce ? false : { y: -80, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: EASE_OUT, delay: 0.1 }}
      className={`fixed inset-x-0 top-0 z-[60] transition-colors duration-500 ${
        solid ? "border-b border-line bg-bg/70 backdrop-blur-xl" : "border-b border-transparent"
      }`}
    >
      <nav className="mx-auto flex max-w-[1320px] items-center justify-between px-5 py-4 sm:px-8">
        <a href="#top" className="flex items-center gap-2.5">
          <Icon name="mark" className="h-7 w-7 text-gold" />
          <span className="font-display text-[16px] font-bold tracking-tight">
            CleanLines <span className="font-medium text-dim">Studio</span>
          </span>
        </a>

        <div className="hidden items-center gap-9 md:flex">
          {LINKS.map((l) => (
            <a
              key={l.href}
              href={l.href}
              className="group relative font-body text-[14px] text-dim transition-colors duration-200 hover:text-ink"
            >
              {l.label}
              <span className="absolute -bottom-1 left-0 h-px w-0 bg-gold transition-[width] duration-300 ease-out group-hover:w-full" />
            </a>
          ))}
        </div>

        <div className="flex items-center gap-3">
          <Button href={`mailto:${MAIL}`} variant="primary" className="hidden px-5 py-2.5 text-[13px] sm:inline-flex" magnetic>
            Preview sichern
          </Button>
          <button
            aria-label="Menü"
            onClick={() => setOpen((v) => !v)}
            className="grid h-10 w-10 cursor-pointer place-items-center rounded-full border border-line md:hidden"
          >
            <span className="relative block h-3 w-4">
              <span
                className={`absolute left-0 top-0 h-[1.5px] w-4 bg-ink transition-transform duration-300 ${open ? "translate-y-[5px] rotate-45" : ""}`}
              />
              <span
                className={`absolute bottom-0 left-0 h-[1.5px] w-4 bg-ink transition-transform duration-300 ${open ? "-translate-y-[5px] -rotate-45" : ""}`}
              />
            </span>
          </button>
        </div>
      </nav>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: EASE_OUT }}
            className="overflow-hidden border-t border-line bg-bg/95 backdrop-blur-xl md:hidden"
          >
            <div className="flex flex-col px-6 py-4">
              {LINKS.map((l) => (
                <a
                  key={l.href}
                  href={l.href}
                  onClick={() => setOpen(false)}
                  className="border-b border-line/60 py-3.5 font-display text-[17px] font-semibold"
                >
                  {l.label}
                </a>
              ))}
              <a
                href={`mailto:${MAIL}`}
                className="mt-4 rounded-full bg-gradient-to-br from-gold to-gold-bright px-5 py-3 text-center font-bold text-[#1a1206]"
              >
                Preview sichern
              </a>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.header>
  );
}
