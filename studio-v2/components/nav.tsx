"use client";

import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";

const LINKS = [
  { href: "#leistungen", label: "Leistungen" },
  { href: "#branchen", label: "Branchen" },
  { href: "#prozess", label: "Prozess" },
  { href: "#pakete", label: "Pakete" },
];

export function Nav() {
  const [solid, setSolid] = useState(false);
  const pathname = usePathname();

  useEffect(() => {
    const onScroll = () => setSolid(window.scrollY > 40);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  if (
    pathname?.startsWith("/atelier") ||
    pathname?.startsWith("/studio") ||
    pathname?.startsWith("/award") ||
    pathname?.startsWith("/experience")
  )
    return null;

  return (
    <header
      className={`fixed inset-x-0 top-0 z-50 transition-all duration-500 ${
        solid
          ? "border-b border-line bg-bg/70 backdrop-blur-xl"
          : "border-b border-transparent"
      }`}
    >
      <nav className="shell flex h-[68px] items-center justify-between" style={{ ["--max" as string]: "1680px" }}>
        <a href="#top" className="flex items-center gap-2.5">
          <span className="grid h-7 w-7 place-items-center rounded-[7px] bg-gradient-to-br from-gold-bright to-gold-deep text-[13px] font-extrabold text-[#1a1206]">
            C
          </span>
          <span className="font-display text-[15px] font-bold tracking-tight">
            Clean Lines <span className="text-muted">Studios</span>
          </span>
        </a>

        <div className="hidden items-center gap-8 md:flex">
          {LINKS.map((l) => (
            <a
              key={l.href}
              href={l.href}
              className="font-body text-[14px] text-dim transition-colors hover:text-ink"
            >
              {l.label}
            </a>
          ))}
        </div>

        <a
          href="#kontakt"
          className="rounded-full bg-ink px-5 py-2.5 font-display text-[13.5px] font-bold text-bg transition-transform duration-300 hover:scale-[1.03]"
        >
          Projekt starten
        </a>
      </nav>
    </header>
  );
}
