"use client";

import { AnimatedHeading, Reveal, Button, ScrollScrub } from "@/components/award/ux";
import { Icon } from "@/components/cl/icons";
import { SERVICES, BRANCHES, PLANS, MAIL } from "@/lib/cl-data";

export function Overlay() {
  return (
    <div className="relative z-10">
      {/* ACT 1 — HERO */}
      <section className="relative flex min-h-screen items-center px-6 sm:px-10">
        <div className="mx-auto w-full max-w-[1320px]">
          <div className="max-w-[620px]">
            <ScrollScrub className="font-mono text-[12px] uppercase tracking-[0.22em] text-gold">
              Creative Content Hub · für lokale Betriebe
            </ScrollScrub>
            <AnimatedHeading
              as="h1"
              lines={[
                "Content, der deinen",
                <span key="g" className="text-gold">
                  Betrieb sichtbar macht.
                </span>,
              ]}
              className="mt-6 font-display text-[clamp(40px,7vw,96px)] font-extrabold leading-[0.96] tracking-[-0.04em]"
            />
            <Reveal delay={0.2}>
              <p className="mt-7 max-w-[460px] text-[clamp(16px,1.3vw,18px)] text-dim">
                Jeden Monat fertige Reel-Ideen, Captions, Google-Beiträge und ein
                klarer Plan — passend zu deinem Betrieb. Scroll durch unser Atelier.
              </p>
            </Reveal>
            <Reveal delay={0.32} className="mt-9">
              <Button href={`mailto:${MAIL}`} variant="primary" magnetic>
                Kostenlose Content-Preview <Icon name="arrow" className="h-4 w-4" />
              </Button>
            </Reveal>
          </div>
          <div className="absolute bottom-10 left-6 flex items-center gap-3 sm:left-10">
            <span className="block h-px w-10 animate-pulse bg-gold" />
            <span className="font-mono text-[10px] uppercase tracking-[0.24em] text-muted">
              Scroll
            </span>
          </div>
        </div>
      </section>

      {/* ACT 2 — LEISTUNGEN */}
      <section
        id="leistungen"
        className="relative flex min-h-screen items-center px-6 sm:px-10"
      >
        <div className="mx-auto w-full max-w-[1320px]">
          <div className="max-w-[620px] lg:ml-auto lg:text-right">
            <ScrollScrub className="font-mono text-[12px] uppercase tracking-[0.22em] text-gold">
              01 — Leistungen
            </ScrollScrub>
            <AnimatedHeading
              as="h2"
              lines={[
                "Alles vorbereitet.",
                <span key="g" className="text-gold">
                  Du musst nur posten.
                </span>,
              ]}
              className="mt-5 font-display text-[clamp(30px,5vw,64px)] font-extrabold leading-[1.04] tracking-[-0.03em]"
            />
            <ul className="mt-8 flex flex-col gap-3.5 lg:items-end">
              {SERVICES.map((s, i) => (
                <Reveal key={s.title} delay={i * 0.06}>
                  <li className="flex items-center gap-3 lg:flex-row-reverse">
                    <Icon name={s.icon as never} className="h-5 w-5 text-gold" />
                    <span className="font-display text-[clamp(18px,2vw,26px)] font-semibold text-dim transition-colors hover:text-ink">
                      {s.title}
                    </span>
                  </li>
                </Reveal>
              ))}
            </ul>
          </div>
        </div>
      </section>

      {/* ACT 3 — BRANCHEN */}
      <section
        id="branchen"
        className="relative flex min-h-screen items-center px-6 sm:px-10"
      >
        <div className="mx-auto w-full max-w-[1320px]">
          <div className="max-w-[620px]">
            <ScrollScrub className="font-mono text-[12px] uppercase tracking-[0.22em] text-gold">
              02 — Branchen
            </ScrollScrub>
            <AnimatedHeading
              as="h2"
              lines={[
                <span key="a">
                  Content, der zu deinem <span className="text-gold">Betrieb</span>{" "}
                  passt.
                </span>,
              ]}
              className="mt-5 max-w-[14ch] font-display text-[clamp(30px,5vw,64px)] font-extrabold leading-[1.04] tracking-[-0.03em]"
            />
            <div className="mt-8 flex max-w-[560px] flex-wrap gap-2.5">
              {BRANCHES.map((b, i) => (
                <Reveal key={b.tab} delay={i * 0.05}>
                  <span className="rounded-full border border-line bg-white/[0.03] px-4 py-2 text-[14px] text-dim backdrop-blur-sm">
                    {b.tab}
                  </span>
                </Reveal>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ACT 4 — PAKETE */}
      <section
        id="pakete"
        className="relative flex min-h-screen items-center px-6 sm:px-10"
      >
        <div className="mx-auto w-full max-w-[1320px]">
          <div className="max-w-[620px] lg:ml-auto lg:text-right">
            <ScrollScrub className="font-mono text-[12px] uppercase tracking-[0.22em] text-gold">
              03 — Pakete
            </ScrollScrub>
            <AnimatedHeading
              as="h2"
              lines={[
                <span key="a">
                  Wähle, wie <span className="text-gold">sichtbar</span> du wirst.
                </span>,
              ]}
              className="mt-5 font-display text-[clamp(30px,5vw,64px)] font-extrabold leading-[1.04] tracking-[-0.03em]"
            />
            <div className="mt-8 flex flex-col gap-3 lg:items-end">
              {PLANS.map((p, i) => (
                <Reveal key={p.name} delay={i * 0.07}>
                  <div className="flex items-baseline gap-4">
                    <span className="font-display text-[clamp(20px,2.4vw,30px)] font-bold">
                      {p.name}
                    </span>
                    <span className="font-display text-[clamp(20px,2.4vw,30px)] font-extrabold text-gold-bright">
                      {p.price}
                    </span>
                    <span className="font-mono text-[12px] text-muted">
                      {p.cadence}
                    </span>
                  </div>
                </Reveal>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ACT 5 — CTA */}
      <section className="relative flex min-h-screen items-center px-6 sm:px-10">
        <div className="mx-auto w-full max-w-[1320px]">
          <div className="mx-auto max-w-[620px] text-center">
            <ScrollScrub className="font-mono text-[12px] uppercase tracking-[0.22em] text-gold">
              Bereit für mehr Sichtbarkeit?
            </ScrollScrub>
            <AnimatedHeading
              as="h2"
              lines={[
                "Dein Betrieb braucht",
                <span key="g" className="text-gold">
                  ein System, das wirkt.
                </span>,
              ]}
              className="mx-auto mt-6 max-w-[18ch] text-center font-display text-[clamp(34px,6vw,78px)] font-extrabold leading-[1.0] tracking-[-0.035em]"
            />
            <Reveal delay={0.25} className="mt-10">
              <Button href={`mailto:${MAIL}`} variant="primary" magnetic>
                Jetzt Preview sichern <Icon name="arrow" className="h-4 w-4" />
              </Button>
            </Reveal>
            <Reveal delay={0.4} className="mt-16">
              <div className="flex items-center justify-center gap-3">
                <Icon name="mark" className="h-7 w-7 text-gold" />
                <span className="font-display text-[15px] font-semibold tracking-[-0.01em] text-dim">
                  CleanLines Studio
                </span>
              </div>
            </Reveal>
          </div>
        </div>
      </section>
    </div>
  );
}
