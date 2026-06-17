import { Suspense, lazy, useEffect, useRef } from "react";
import { hero, mailto } from "../../content/siteContent";
import MagneticButton from "../ui/MagneticButton";
import BrandMark from "../ui/BrandMark";
import ErrorBoundary from "../ui/ErrorBoundary";
import { scrollToTarget } from "../../motion/lenis";
import { playHeroIntro, buildHeroScroll } from "../../motion/heroTimeline";
import { gsap } from "../../motion/scrollTriggers";

const HeroCanvas = lazy(() => import("../../experience/HeroCanvas"));

interface Props {
  ready: boolean;
}

const CC_TILES = [
  { k: "REELS", v: "Cinematic" },
  { k: "KI-VISUALS", v: "Generativ" },
  { k: "CAPTIONS", v: "On-Brand" },
  { k: "MONATSPLAN", v: "Aktiv" },
];

/** Scene 2 — Hero / WebGL Content Engine + iPad Control Center. Main wow moment. */
export default function HeroSection({ ready }: Props) {
  const root = useRef<HTMLElement>(null);
  const ipadVideo = useRef<HTMLVideoElement>(null);
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
    ipadVideo.current?.play().catch(() => {});
  }, [ready]);

  // Pointer-reactive depth parallax on the DOM layers (floats + watermark).
  useEffect(() => {
    const el = root.current;
    if (!el) return;
    if (window.matchMedia("(pointer: coarse), (prefers-reduced-motion: reduce)").matches) return;
    let raf = 0;
    let tx = 0;
    let ty = 0;
    const onMove = (e: MouseEvent) => {
      tx = (e.clientX / window.innerWidth - 0.5) * 2;
      ty = (e.clientY / window.innerHeight - 0.5) * 2;
      if (!raf)
        raf = requestAnimationFrame(() => {
          el.style.setProperty("--mx", tx.toFixed(3));
          el.style.setProperty("--my", ty.toFixed(3));
          raf = 0;
        });
    };
    window.addEventListener("mousemove", onMove);
    return () => {
      window.removeEventListener("mousemove", onMove);
      if (raf) cancelAnimationFrame(raf);
    };
  }, []);

  return (
    <section className="hero section" id="hero" ref={root}>
      <ErrorBoundary fallback={<div className="hero__canvas hero__canvas--fallback" />}>
        <Suspense fallback={<div className="hero__canvas hero__canvas--fallback" />}>
          <HeroCanvas />
        </Suspense>
      </ErrorBoundary>

      <div className="hero__watermark" aria-hidden>
        STUDIOS
      </div>

      {/* Floating UI proof-satellites — subtle depth + conversion micro-proof */}
      <div className="hero__floats" aria-hidden>
        <div className="hfloat hfloat--a">
          <span className="hfloat__dot" />
          <div>
            <b>+38%</b>
            <small>Sichtbarkeit</small>
          </div>
        </div>
        <div className="hfloat hfloat--b">
          <span className="hfloat__check">✓</span>
          <div>
            <b>Reel geplant</b>
            <small>Mo · 18:00</small>
          </div>
        </div>
        <div className="hfloat hfloat--c">
          <span className="hfloat__dot hfloat__dot--gold" />
          <div>
            <b>Bewertung beantwortet</b>
            <small>★ 5,0 · heute</small>
          </div>
        </div>
      </div>

      <div className="hero__inner shell">
        <div className="hero__col">
          <div className="hero__eyebrow eyebrow">{hero.eyebrow}</div>
          <h1 className="hero__headline headline-hero">{hero.headline}</h1>
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

        {/* Compact Control Center card — composited over the WebGL logo */}
        <div className="hero__ipad" aria-hidden>
            <div className="ipad">
              <div className="ipad__frame">
                <span className="ipad__cam" />
                <div className="ipad__screen">
                  <video
                    ref={ipadVideo}
                    src="/assets/videos/hero.mp4"
                    muted
                    loop
                    playsInline
                    autoPlay
                    preload="auto"
                  />
                  <div className="ipad__scrim" />
                  <div className="ipad__os">
                    <div className="cc-top">
                      <BrandMark />
                      <span className="cc-live">
                        <i /> LIVE
                      </span>
                    </div>
                    <div className="cc-tiles">
                      {CC_TILES.map((t) => (
                        <div className="cc-tile" key={t.k}>
                          <span className="cc-tile__k">{t.k}</span>
                          <span className="cc-tile__v">{t.v}</span>
                        </div>
                      ))}
                    </div>
                    <div className="cc-bar">
                      <span>CONTENT CONTROL CENTER</span>
                      <span className="cc-bar__pct">100%</span>
                    </div>
                  </div>
                </div>
              </div>
              <span className="ipad__reflect" />
            </div>
          </div>
        <div className="hero__hudbar">
          <div className="hud-row">
            <span className="hud-dot" />
            <b>{hero.hud.status}</b>
          </div>
          <div className="hud-row">{hero.hud.pipeline}</div>
          <div className="hud-row">{hero.hud.location}</div>
        </div>
      </div>

      <div className="hero__scroll">
        SCROLL
        <i />
      </div>
    </section>
  );
}
