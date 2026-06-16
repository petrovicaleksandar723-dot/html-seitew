import { Suspense, lazy, useEffect, useRef } from "react";
import { HERO } from "../../content/siteContent";
import { MagneticButton } from "../ui/MagneticButton";
import { Boundary } from "../ui/Boundary";
import { buildHeroIntro } from "../../motion/heroTimeline";
import { gsap } from "../../motion/scrollTriggers";

const HeroCanvas = lazy(() => import("../../experience/HeroCanvas"));

export function HeroSection() {
  const ref = useRef<HTMLElement>(null);

  useEffect(() => {
    const scope = ref.current;
    if (!scope) return;
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const ctx = gsap.context(() => {
      if (reduce) {
        scope.querySelectorAll<HTMLElement>("[data-fade]").forEach((e) => (e.style.opacity = "1"));
      } else {
        buildHeroIntro(scope, 0.55);
      }
    }, scope);
    return () => ctx.revert();
  }, []);

  return (
    <section id="hero" ref={ref}>
      <Boundary fallback={<div className="hero-fallback" aria-hidden />}>
        <Suspense fallback={<div className="hero-fallback" aria-hidden />}>
          <HeroCanvas />
        </Suspense>
      </Boundary>

      <div className="hero-bgtype" aria-hidden>
        ENGINE
      </div>

      <div className="wrap hero-inner">
        <div className="hero-top">
          <span className="klabel" data-fade>
            {HERO.tickerTop}
          </span>
          <div className="hero-ticker">
            <span className="klabel r" data-fade>
              {HERO.tickerMid}
            </span>
            <span className="klabel r faint" data-fade>
              {HERO.tickerLow}
            </span>
          </div>
        </div>

        <div className="hero-headline">
          <span className="hero-hud" data-fade>
            <i /> {HERO.hud}
          </span>
          <h1 className="h-hero">
            <span className="line-mask">
              <span className="hero-line">{HERO.headline[0]}</span>
            </span>
            <span className="line-mask">
              <span className="hero-line">{HERO.headline[1]}</span>
            </span>
            <span className="line-mask">
              <span className="hero-line gold-text">{HERO.headline[2]}</span>
            </span>
          </h1>
        </div>

        <div className="hero-foot">
          <div className="hero-lede-col">
            <p className="lede" data-fade>
              {HERO.subline}
            </p>
            <div className="hero-actions" data-fade>
              <MagneticButton to="final" variant="primary">
                {HERO.primary}
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round">
                  <path d="M5 12h14M13 6l6 6-6 6" />
                </svg>
              </MagneticButton>
              <MagneticButton to="showcase" variant="ghost">
                {HERO.secondary}
              </MagneticButton>
            </div>
          </div>
          <div className="hero-status" data-fade>
            {HERO.stats.map((s) => (
              <div className="stat" key={s.label}>
                <b>{s.value}</b>
                <span>{s.label}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="scroll-hint" aria-hidden>
        <span className="bar" /> Scroll
      </div>
    </section>
  );
}
