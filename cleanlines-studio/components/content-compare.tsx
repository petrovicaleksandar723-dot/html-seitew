"use client";

import { Reveal } from "@/components/ui/reveal";
import { AnimatedHeading } from "@/components/ui/animated-heading";
import { MediaBackdrop } from "@/components/ui/media-backdrop";
import { asset } from "@/lib/asset";

const EXAMPLES = [
  asset("/videos/example-1.mp4"),
  asset("/videos/example-2.mp4"),
  asset("/videos/example-3.mp4"),
  asset("/videos/example-4.mp4"),
];

const CONS = [
  "Unregelmäßige Posts, kein roter Faden",
  "Stundenlang filmen, schneiden, texten — neben dem Tagesgeschäft",
  "Sieht schnell billig oder zufällig aus",
  "Keine Strategie, keine Wiedererkennung",
  "Anfragen bleiben aus",
];

const PROS = [
  "Fertiger Monatsplan — du weißt immer, was kommt",
  "Hochwertige Reels, Captions & Visuals, einsatzbereit",
  "Einheitlicher Premium-Look, der Vertrauen schafft",
  "Klare Content-Strategie, passend zu deiner Branche",
  "Mehr Sichtbarkeit — und am Ende mehr Anfragen",
];

export function ContentCompare() {
  return (
    <section
      id="beispiele"
      className="relative overflow-hidden py-[clamp(100px,15vw,180px)]"
    >
      {/* background montage — 4 example clips */}
      <MediaBackdrop videos={EXAMPLES} opacity={0.34} />

      <div className="shell content relative z-10">
        <div className="max-w-[760px]">
          <Reveal>
            <span className="eyebrow">Vorher / Nachher · Beispiele</span>
          </Reveal>
          <AnimatedHeading
            className="mt-6 font-display text-[clamp(32px,5vw,60px)] font-bold leading-[1.02] tracking-[-0.02em]"
            lines={[
              [{ t: "Selbst probieren — oder ein" }],
              [{ t: "System, das einfach läuft.", accent: true }],
            ]}
          />
          <Reveal delay={0.1}>
            <p className="mt-6 max-w-[620px] font-body text-[17px] leading-relaxed text-dim">
              So könnte dein Content aussehen. Die Clips im Hintergrund sind
              Beispiele — und werden später durch deinen echten Content ersetzt.
            </p>
          </Reveal>
        </div>

        <div className="mt-14 grid gap-5 lg:grid-cols-2">
          {/* Nachteile */}
          <Reveal delay={0.05}>
            <div className="h-full rounded-2xl border border-line bg-bg/40 p-8 backdrop-blur-md">
              <div className="flex items-center gap-3">
                <span className="grid h-9 w-9 place-items-center rounded-full border border-white/15 text-[18px] text-muted">
                  ✕
                </span>
                <div>
                  <div className="font-mono text-[10px] uppercase tracking-[0.2em] text-muted">
                    Ohne System
                  </div>
                  <div className="font-display text-[19px] font-bold tracking-tight">
                    Selbst gemacht
                  </div>
                </div>
              </div>
              <ul className="mt-7 space-y-4">
                {CONS.map((c) => (
                  <li
                    key={c}
                    className="flex items-start gap-3 font-body text-[15px] text-dim/85"
                  >
                    <span className="mt-0.5 text-[14px] text-muted">✕</span>
                    {c}
                  </li>
                ))}
              </ul>
            </div>
          </Reveal>

          {/* Vorteile */}
          <Reveal delay={0.12}>
            <div className="glass relative h-full overflow-hidden rounded-2xl p-8">
              <div className="lightfield -right-10 -top-10 h-56 w-56 bg-gold/15" />
              <div className="relative flex items-center gap-3">
                <span className="grid h-9 w-9 place-items-center rounded-full bg-gradient-to-br from-gold-bright to-gold-deep text-[16px] text-[#1a1206]">
                  ✓
                </span>
                <div>
                  <div className="font-mono text-[10px] uppercase tracking-[0.2em] text-gold">
                    Mit Cleanlines
                  </div>
                  <div className="font-display text-[19px] font-bold tracking-tight">
                    Ein System, das läuft
                  </div>
                </div>
              </div>
              <ul className="relative mt-7 space-y-4">
                {PROS.map((p) => (
                  <li
                    key={p}
                    className="flex items-start gap-3 font-body text-[15px] text-ink"
                  >
                    <span className="mt-0.5 text-gold">✓</span>
                    {p}
                  </li>
                ))}
              </ul>
            </div>
          </Reveal>
        </div>

        <Reveal delay={0.1}>
          <p className="mt-8 flex items-center gap-2 font-mono text-[11px] uppercase tracking-[0.18em] text-muted">
            <span className="h-1.5 w-1.5 rounded-full bg-gold" />
            Beispiel-Clips · werden durch deinen echten Content ersetzt
          </p>
        </Reveal>
      </div>
    </section>
  );
}
