"use client";

import { Reveal } from "@/components/award/ux";
import { Icon } from "@/components/cl/icons";
import { MAIL } from "@/lib/cl-data";

const NAV = [
  { label: "Leistungen", href: "#leistungen" },
  { label: "Branchen", href: "#branchen" },
  { label: "Pakete", href: "#pakete" },
  { label: "FAQ", href: "#faq" },
];

export function AwFooter() {
  return (
    <footer className="border-t border-line bg-bg">
      <div className="mx-auto max-w-[1320px] px-5 py-16 sm:px-8">
        <Reveal>
          <div className="mt-4 grid gap-10 md:grid-cols-[1.5fr_1fr_1fr]">
            <div>
              <div className="flex items-center gap-3">
                <Icon name="mark" className="h-9 w-9 text-gold" />
                <span className="font-display text-[20px] font-bold">
                  CleanLines <span className="font-medium text-dim">Studio</span>
                </span>
              </div>
              <p className="mt-4 max-w-[320px] text-[14px] text-dim">
                Creative Content Hub für lokale Betriebe – Reels, Captions und ein
                klarer Plan, jeden Monat.
              </p>
            </div>

            <div>
              <h3 className="font-mono text-[11px] uppercase tracking-[0.18em] text-muted">
                Navigation
              </h3>
              <nav className="mt-2">
                {NAV.map((n) => (
                  <a
                    key={n.href}
                    href={n.href}
                    className="block cursor-pointer py-1.5 text-[14px] text-dim transition-colors hover:text-ink"
                  >
                    {n.label}
                  </a>
                ))}
              </nav>
            </div>

            <div>
              <h3 className="font-mono text-[11px] uppercase tracking-[0.18em] text-muted">
                Kontakt
              </h3>
              <a
                href={`mailto:${MAIL}`}
                className="mt-2 block cursor-pointer py-1.5 text-[14px] text-gold-bright"
              >
                {MAIL}
              </a>
              <p className="py-1.5 text-[14px] text-muted">Antwort in 24 Std.</p>
            </div>
          </div>
        </Reveal>

        <div className="mt-14 flex flex-col items-center justify-between gap-4 border-t border-line pt-7 sm:flex-row">
          <p className="text-[13px] text-muted">
            © 2026 CleanLines Studio. Alle Rechte vorbehalten.
          </p>
          <a
            href="#top"
            className="inline-flex cursor-pointer items-center gap-2 text-[13px] text-dim transition-colors hover:text-ink"
          >
            Nach oben
            <Icon name="arrow" className="h-3.5 w-3.5 -rotate-90" />
          </a>
        </div>
      </div>
    </footer>
  );
}
