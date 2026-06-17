import { Suspense, lazy, useEffect, useRef } from "react";
import { hero, mailto, contact } from "../../content/siteContent";
import MagneticButton from "../ui/MagneticButton";
import ErrorBoundary from "../ui/ErrorBoundary";
import { scrollToTarget } from "../../motion/lenis";
import { playHeroIntro, buildHeroScroll } from "../../motion/heroTimeline";
import { gsap } from "../../motion/scrollTriggers";

const HeroCanvas = lazy(() => import("../../experience/HeroCanvas"));

interface Props {
  ready: boolean;
}

/** Scene 1 — Editorial hero: serif statement + large cinematic video. */
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
      <div className="hero__inner shell">
        <div className="hero__topline">
          <span className="hero__index">Cleanlines Studios — Index</span>
          <span className="hero__loc">{contact.location} · Est. 2025</span>
        </div>

        <div className="hero__main">
          <div className="hero__col">
            <div className="hero__eyebrow eyebrow">{hero.eyebrow}</div>
            <h1 className="hero__headline headline-hero">{hero.headline}</h1>
            <div className="hero__bottom">
              <p className="hero__lead">{hero.subline}</p>
              <div className="hero__cta">
                <MagneticButton href={mailto("Kostenlose Content-Preview")}>
                  {hero.ctaPrimary}
                </MagneticButton>
                <MagneticButton variant="ghost" onClick={() => scrollToTarget("#reel-cinema")}>
                  {hero.ctaSecondary}
                </MagneticButton>
              </div>
            </div>
          </div>

          <figure className="hero__media hero3d">
            <ErrorBoundary
              fallback={
                <video
                  src="/assets/videos/hero.mp4"
                  muted
                  loop
                  playsInline
                  autoPlay
                  preload="auto"
                  aria-hidden="true"
                />
              }
            >
              <Suspense fallback={<div className="hero3d__loading" />}>
                <HeroCanvas />
              </Suspense>
            </ErrorBoundary>
            <figcaption className="hero__media-cap">
              <span>Cleanlines · 3D Mark</span>
              <span className="hero__drag">↻ Ziehen zum Drehen</span>
            </figcaption>
          </figure>
        </div>

        <div className="hero__meta">
          {hero.trust.map((t) => (
            <span key={t}>{t}</span>
          ))}
          <span className="hero__meta-spacer" />
          <span className="hero__meta-hud">{hero.hud.pipeline}</span>
        </div>
      </div>

      <div className="hero__scroll" aria-hidden>
        <span>Scroll</span>
        <i />
      </div>
    </section>
  );
}
