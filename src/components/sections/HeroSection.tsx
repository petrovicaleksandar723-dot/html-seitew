import { Suspense, lazy, useEffect, useRef } from "react";
import { HERO } from "../../content/siteContent";
import { MagneticButton } from "../ui/MagneticButton";
import { Boundary } from "../ui/Boundary";
import { VideoPanel } from "../ui/VideoPanel";
import { IpadFrame } from "../ui/IpadFrame";
import { buildHeroIntro } from "../../motion/heroTimeline";
import { gsap } from "../../motion/scrollTriggers";

const HeroCanvas = lazy(() => import("../../experience/HeroCanvas"));

export function HeroSection() {
  const ref = useRef<HTMLElement>(null);
  const ipadWrap = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const scope = ref.current;
    if (!scope) return;
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const ctx = gsap.context(() => {
      if (reduce) {
        scope.querySelectorAll<HTMLElement>("[data-fade]").forEach((e) => (e.style.opacity = "1"));
        if (ipadWrap.current) ipadWrap.current.style.opacity = "1";
        return;
      }
      buildHeroIntro(scope, 0.55);
      if (ipadWrap.current) {
        gsap.fromTo(
          ipadWrap.current,
          { opacity: 0, x: 50, rotateY: -10 },
          { opacity: 1, x: 0, rotateY: 0, duration: 1.4, ease: "expo.out", delay: 0.85 }
        );
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
            <div className="hero-stats-row" data-fade>
              {HERO.stats.map((s) => (
                <div className="stat" key={s.label}>
                  <b>{s.value}</b>
                  <span>{s.label}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Large premium iPad intro — plays the CleanLines promo, with floating video panels */}
      <div className="hero-ipad-wrap" ref={ipadWrap}>
        <div className="hero-frags" aria-hidden>
          <VideoPanel src="/assets/videos/reel-2.mp4" className="hero-frag f1" />
          <VideoPanel src="/assets/videos/show-2.mp4" className="hero-frag f2" />
        </div>
        <div className="hero-ipad">
          <IpadFrame>
            <div className="hero-ipad-screen">
              <video src="/assets/videos/hero.mp4" autoPlay muted loop playsInline preload="metadata" />
              <div className="hero-ipad-veil" />
              <div className="hero-ipad-logo">
                CleanLines<span className="gold-text">.</span>
                <small>STUDIO</small>
              </div>
              <div className="hero-ipad-badge">
                <i /> Showreel
              </div>
            </div>
          </IpadFrame>
        </div>
      </div>

      <div className="scroll-hint" aria-hidden>
        <span className="bar" /> Scroll
      </div>
    </section>
  );
}
