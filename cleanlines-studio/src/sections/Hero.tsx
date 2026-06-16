import { Suspense, lazy } from "react";
import { Reveal } from "../motion/Reveal";
import { Button } from "../components/Button";
import { MAIL } from "../data/content";

const HeroScene = lazy(() => import("../experience/HeroScene").then((m) => ({ default: m.HeroScene })));

export function Hero() {
  return (
    <section className="hero" id="top">
      <div className="hero-canvas">
        <Suspense fallback={null}>
          <HeroScene />
        </Suspense>
      </div>
      <div className="hero-veil" />
      <div className="hero-chip c1">
        <b>▶</b> Reel · fertig geschnitten
      </div>
      <div className="hero-chip c2">
        <b>◆</b> Monatsplan · klar
      </div>
      <div className="wrap">
        <div className="hero-inner">
          <Reveal>
            <span className="eyebrow">Cinematisches Content-Studio</span>
            <h1 className="h1">
              Wir machen lokale Betriebe zu <span className="shine">Premium-Marken.</span>
            </h1>
            <p className="sub" style={{ marginTop: 18 }}>
              Cinematische Reels, KI-Content und ein klares System – damit dein Betrieb online endlich so hochwertig wirkt, wie er wirklich ist.
            </p>
          </Reveal>
          <Reveal delay={0.15}>
            <div className="btns">
              <Button href={MAIL}>Kostenlose Content-Preview</Button>
              <Button href="#showcase" variant="ghost">
                Showreel ansehen
              </Button>
            </div>
            <div className="trust">
              <span>Unverbindlich</span>
              <span>Persönlicher Kontakt</span>
              <span>Monatlich kündbar</span>
            </div>
            <div className="scrollcue">
              <span className="m" />
              Scroll
            </div>
          </Reveal>
        </div>
      </div>
    </section>
  );
}
