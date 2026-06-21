"use client";

import { Reveal, Marquee } from "@/components/award/ux";

const WORDS = [
  "Friseure",
  "Restaurants",
  "Handwerk",
  "Kosmetikstudios",
  "Fahrschulen",
  "Fitnessstudios",
  "Cafés",
  "Zahnärzte",
  "Immobilien",
  "Floristik",
];

export function AwLogos() {
  return (
    <section className="border-y border-line py-10">
      <Reveal className="mb-7 text-center font-mono text-[11px] uppercase tracking-[0.22em] text-muted">
        Vertraut von 120+ lokalen Betrieben
      </Reveal>

      <div className="relative">
        {/* edge fade masks */}
        <div
          aria-hidden
          className="pointer-events-none absolute inset-y-0 left-0 z-10 w-24 bg-gradient-to-r from-bg to-transparent"
        />
        <div
          aria-hidden
          className="pointer-events-none absolute inset-y-0 right-0 z-10 w-24 bg-gradient-to-l from-bg to-transparent"
        />

        <Marquee speed={34}>
          {WORDS.map((word) => (
            <div key={word} className="flex items-center gap-7">
              <span className="font-display text-[clamp(20px,2vw,30px)] font-semibold text-dim/80">
                {word}
              </span>
              <span aria-hidden className="h-1.5 w-1.5 rounded-full bg-gold/50" />
            </div>
          ))}
        </Marquee>
      </div>
    </section>
  );
}
