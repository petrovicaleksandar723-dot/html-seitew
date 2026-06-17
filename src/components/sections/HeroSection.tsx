import { Suspense, lazy, useEffect, useRef } from "react";
import { hero, mailto } from "../../content/siteContent";
import MagneticButton from "../ui/MagneticButton";
import BrandMark from "../ui/BrandMark";
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

  return (
    <section className="hero section" id="hero" ref={root}>
      <Suspense fallback={null}>
        <HeroCanvas />
      </Suspense>

      <div className="hero__inner shell">
        <div className="hero__grid">
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

          {/* iPad / Control Center — DOM composited over the WebGL engine */}
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
