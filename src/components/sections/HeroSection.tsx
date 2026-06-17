import { Suspense, lazy, useEffect, useRef } from "react";
import { hero } from "../../content/siteContent";
import { mailto } from "../../content/siteContent";
import MagneticButton from "../ui/MagneticButton";
import { scrollToTarget } from "../../motion/lenis";
import { playHeroIntro, buildHeroScroll } from "../../motion/heroTimeline";
import { gsap } from "../../motion/scrollTriggers";

const HeroCanvas = lazy(() => import("../../experience/HeroCanvas"));

interface Props {
  ready: boolean;
}

/** Scene 2 — Hero / WebGL Content Engine. The main wow moment. */
export default function HeroSection({ ready }: Props) {
  const root = useRef<HTMLElement>(null);
  const played = useRef(false);

  useEffect(() => {
    const el = root.current;
    if (!el) return;
    const ctx = gsap.context(() => buildHeroScroll(el), el);
    return () => ctx.revert();
  }, []);

  useEffect(() => {
    if (!ready || played.current || !root.current) return;
    played.current = true;
    playHeroIntro(root.current);
  }, [ready]);

  return (
    <section className="hero section" id="hero" ref={root}>
      <Suspense fallback={null}>
        <HeroCanvas />
      </Suspense>

      <div className="hero__inner shell">
        <div className="hero__eyebrow eyebrow">{hero.eyebrow}</div>

        <h1 className="hero__headline headline-hero">{hero.headline}</h1>

        <div className="hero__bottom">
          <div>
            <p className="hero__subline">{hero.subline}</p>
            <div className="hero__cta">
              <MagneticButton href={mailto("Kostenlose Content-Preview")}>
                {hero.ctaPrimary}
              </MagneticButton>
              <MagneticButton variant="ghost" onClick={() => scrollToTarget("#reel-cinema")}>
                {hero.ctaSecondary}
              </MagneticButton>
            </div>
            <div className="hero__trust">
              {hero.trust.map((t) => (
                <span key={t}>{t}</span>
              ))}
            </div>
          </div>

          <div className="hero__hud">
            <div className="hud-row">
              <span className="hud-dot" />
              <b>{hero.hud.status}</b>
            </div>
            <div className="hud-row">{hero.hud.pipeline}</div>
            <div className="hud-row">{hero.hud.location}</div>
          </div>
        </div>
      </div>

      <div className="hero__scroll">
        SCROLL
        <i />
      </div>
    </section>
  );
}
