import { useEffect, useRef, useState } from "react";
import { Play, Pause, Volume2, VolumeX } from "lucide-react";
import { reelCinema } from "../../content/siteContent";
import SectionNumber from "../ui/SectionNumber";
import { buildReelCinema } from "../../motion/reelCinemaTimeline";
import { gsap } from "../../motion/scrollTriggers";

/** Scene 5 — Reel Cinema. Pinned horizontal scroll, cinematic active reel. */
export default function ReelCinemaSection() {
  const section = useRef<HTMLElement>(null);
  const track = useRef<HTMLDivElement>(null);
  const videos = useRef<(HTMLVideoElement | null)[]>([]);
  const [active, setActive] = useState(0);
  const [muted, setMuted] = useState(true);
  const [paused, setPaused] = useState(false);

  // build the pinned horizontal scroll
  useEffect(() => {
    const sec = section.current;
    const trk = track.current;
    if (!sec || !trk) return;
    if (window.matchMedia("(pointer: coarse)").matches) return; // desktop-first pin

    const ctx = gsap.context(() => {
      buildReelCinema(sec, trk, reelCinema.reels.length, {
        onActive: (idx) => setActive(idx),
      });
    }, sec);
    return () => ctx.revert();
  }, []);

  // play only the active reel
  useEffect(() => {
    videos.current.forEach((v, i) => {
      if (!v) return;
      if (i === active && !paused) {
        v.play().catch(() => {});
      } else {
        v.pause();
      }
      v.muted = muted;
    });
  }, [active, muted, paused]);

  const togglePlay = () => {
    const v = videos.current[active];
    if (!v) return;
    if (v.paused) {
      v.play().catch(() => {});
      setPaused(false);
    } else {
      v.pause();
      setPaused(true);
    }
  };

  return (
    <section className="cinema section" id="reel-cinema" ref={section}>
      <div className="cinema__pin">
        <div className="cinema__ambient" />
        <div className="cinema__head shell" style={{ paddingInline: 0 }}>
          <div className="scene-head" style={{ gap: 16 }}>
            <SectionNumber num="03" label="Reel Cinema" />
            <div className="eyebrow">{reelCinema.eyebrow}</div>
            <h2 className="headline-section" style={{ fontSize: "clamp(40px,4vw,72px)" }}>
              {reelCinema.headline}
            </h2>
          </div>
          <div className="cinema__count">
            <b>{String(active + 1).padStart(2, "0")}</b> / {String(reelCinema.reels.length).padStart(2, "0")}
          </div>
        </div>

        <div className="cinema__track" ref={track}>
          {reelCinema.reels.map((reel, i) => (
            <article key={reel.src} className={`reel-card ${i === active ? "is-active" : ""}`}>
              <span className="reel-card__num">{reel.index}</span>
              <video
                ref={(el) => {
                  videos.current[i] = el;
                }}
                src={reel.src}
                muted
                loop
                playsInline
                preload="metadata"
              />
              <div className="reel-card__scrim" />
              <div className="reel-card__gold" />
              <div className="reel-card__meta">
                <div>
                  <div className="t">{reel.title}</div>
                  <div className="m">{reel.meta}</div>
                </div>
              </div>
            </article>
          ))}
        </div>

        <div className="cinema__floor" />

        <div className="cinema__controls">
          <button className="cine-btn" onClick={togglePlay} aria-label="Play/Pause" data-cursor="hover">
            {paused ? <Play size={18} /> : <Pause size={18} />}
          </button>
          <button
            className="cine-btn"
            onClick={() => setMuted((m) => !m)}
            aria-label="Ton an/aus"
            data-cursor="hover"
          >
            {muted ? <VolumeX size={18} /> : <Volume2 size={18} />}
          </button>
        </div>
      </div>
    </section>
  );
}
