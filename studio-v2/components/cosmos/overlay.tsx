"use client";

import { AnimatedHeading, Reveal, Button } from "@/components/award/ux";
import { Icon } from "@/components/cl/icons";
import { SERVICES, BRANCHES, PLANS, MAIL } from "@/lib/cl-data";

function Act({
  children,
  align = "left",
  className = "",
}: {
  children: React.ReactNode;
  align?: "left" | "right" | "center";
  className?: string;
}) {
  const place =
    align === "right" ? "lg:ml-auto lg:text-right lg:items-end" : align === "center" ? "mx-auto text-center items-center" : "items-start";
  return (
    <section className={`relative flex min-h-screen items-center px-6 sm:px-10 ${className}`}>
      <div className="mx-auto w-full max-w-[1320px]">
        <div className={`flex max-w-[640px] flex-col ${place}`}>{children}</div>
      </div>
    </section>
  );
}

export function Overlay() {
  return (
    <div className="relative z-10">
      {/* ACT 1 — HERO */}
      <Act align="left" className="min-h-[100svh]">
        <Reveal>
          <span className="font-mono text-[12px] uppercase tracking-[0.22em] text-gold">
            Creative Content Hub · für lokale Betriebe
          </span>
        </Reveal>
        <AnimatedHeading
          as="h1"
          lines={[
            "Content, der deinen",
            <span key="g" className="text-gold">
              Betrieb sichtbar macht.
            </span>,
          ]}
          className="mt-6 font-display text-[clamp(38px,7vw,92px)] font-extrabold leading-[0.98] tracking-[-0.04em]"
        />
        <Reveal delay={0.2}>
          <p className="mt-7 max-w-[480px] font-body text-[clamp(16px,1.3vw,18px)] leading-relaxed text-dim">
            Jeden Monat fertige Reel-Ideen, Captions, Google-Beiträge und ein klarer
            Plan — passend zu deinem Betrieb. Scroll durch unser Atelier.
          </p>
        </Reveal>
        <Reveal delay={0.32} className="mt-9">
          <Button href={`mailto:${MAIL}`} variant="primary" magnetic>
            Kostenlose Content-Preview <Icon name="arrow" className="h-4 w-4" />
          </Button>
        </Reveal>
        <div className="mt-16 flex items-center gap-2.5 font-mono text-[10px] uppercase tracking-[0.24em] text-muted">
          <span className="h-8 w-px animate-pulse bg-gradient-to-b from-gold to-transparent" />
          Scroll
        </div>
      </Act>

      {/* ACT 2 — LEISTUNGEN */}
      <Act align="right">
        <Reveal>
          <span className="font-mono text-[12px] uppercase tracking-[0.2em] text-gold">01 — Leistungen</span>
        </Reveal>
        <AnimatedHeading
          as="h2"
          lines={["Alles vorbereitet.", <span key="g" className="text-gold">Du musst nur posten.</span>]}
          className="mt-5 font-display text-[clamp(30px,5vw,64px)] font-extrabold leading-[1.04] tracking-[-0.03em]"
        />
        <ul className="mt-8 flex flex-col gap-3.5 lg:items-end">
          {SERVICES.map((s, i) => (
            <Reveal key={s.title} delay={i * 0.06}>
              <li className="flex items-center gap-3 font-display text-[clamp(18px,2vw,26px)] font-semibold text-dim transition-colors hover:text-ink">
                <Icon name={s.icon as never} className="h-5 w-5 text-gold" />
                {s.title}
              </li>
            </Reveal>
          ))}
        </ul>
      </Act>

      {/* ACT 3 — BRANCHEN */}
      <Act align="left">
        <Reveal>
          <span className="font-mono text-[12px] uppercase tracking-[0.2em] text-gold">02 — Branchen</span>
        </Reveal>
        <AnimatedHeading
          as="h2"
          lines={[<span key="a">Content, der zu deinem <span className="text-gold">Betrieb</span> passt.</span>]}
          className="mt-5 max-w-[14ch] font-display text-[clamp(30px,5vw,64px)] font-extrabold leading-[1.04] tracking-[-0.03em]"
        />
        <div className="mt-8 flex max-w-[560px] flex-wrap gap-2.5">
          {BRANCHES.map((b, i) => (
            <Reveal key={b.tab} delay={i * 0.05}>
              <span className="rounded-full border border-line bg-white/[0.03] px-4 py-2 font-body text-[14px] text-dim backdrop-blur-sm">
                {b.tab}
              </span>
            </Reveal>
          ))}
        </div>
      </Act>

      {/* ACT 4 — PAKETE */}
      <Act align="right">
        <Reveal>
          <span className="font-mono text-[12px] uppercase tracking-[0.2em] text-gold">03 — Pakete</span>
        </Reveal>
        <AnimatedHeading
          as="h2"
          lines={[<span key="a">Wähle, wie <span className="text-gold">sichtbar</span> du wirst.</span>]}
          className="mt-5 font-display text-[clamp(30px,5vw,64px)] font-extrabold leading-[1.04] tracking-[-0.03em]"
        />
        <div className="mt-8 flex flex-col gap-3 lg:items-end">
          {PLANS.map((p, i) => (
            <Reveal key={p.name} delay={i * 0.07}>
              <div className="flex items-baseline gap-4">
                <span className="font-display text-[clamp(20px,2.4vw,30px)] font-bold">{p.name}</span>
                <span className="font-display text-[clamp(20px,2.4vw,30px)] font-extrabold text-gold-bright">{p.price}</span>
                <span className="font-mono text-[12px] text-muted">{p.cadence}</span>
              </div>
            </Reveal>
          ))}
        </div>
        <Reveal delay={0.3} className="mt-9 lg:self-end">
          <Button href="/award" variant="ghost">
            Alle Details ansehen <Icon name="arrow" className="h-4 w-4" />
          </Button>
        </Reveal>
      </Act>

      {/* ACT 5 — CTA */}
      <Act align="center" className="min-h-[100svh]">
        <Reveal>
          <span className="font-mono text-[12px] uppercase tracking-[0.22em] text-gold">Bereit für mehr Sichtbarkeit?</span>
        </Reveal>
        <AnimatedHeading
          as="h2"
          lines={["Dein Betrieb braucht", <span key="g" className="text-gold">ein System, das wirkt.</span>]}
          className="mx-auto mt-6 max-w-[18ch] text-center font-display text-[clamp(34px,6vw,78px)] font-extrabold leading-[1.0] tracking-[-0.035em]"
        />
        <Reveal delay={0.25} className="mt-10">
          <Button href={`mailto:${MAIL}`} variant="primary" magnetic>
            Jetzt Preview sichern <Icon name="arrow" className="h-4 w-4" />
          </Button>
        </Reveal>
        <div className="mt-20 flex items-center gap-2.5">
          <Icon name="mark" className="h-7 w-7 text-gold" />
          <span className="font-display text-[14px] font-bold">
            CleanLines <span className="text-dim">Studio</span>
          </span>
        </div>
      </Act>
    </div>
  );
}
