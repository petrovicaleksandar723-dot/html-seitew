import { useEffect, useRef, useState } from "react";
import { Play, Pause, Volume2, VolumeX } from "lucide-react";
import { REELS, REELCINEMA } from "../../content/siteContent";
import { buildReelCinema } from "../../motion/reelCinemaTimeline";
import { gsap } from "../../motion/scrollTriggers";

export function ReelCinemaSection() {
  const sectionRef = useRef<HTMLElement>(null);
  const trackRef = useRef<HTMLDivElement>(null);
  const countRef = useRef<HTMLSpanElement>(null);
  const fillRef = useRef<HTMLDivElement>(null);
  const cardsRef = useRef<HTMLElement[]>([]);
  const videosRef = useRef<(HTMLVideoElement | null)[]>([]);
  const [active, setActive] = useState(0);
  const [muted, setMuted] = useState(true);
  const [paused, setPaused] = useState(false);

  useEffect(() => {
    const section = sectionRef.current;
    const track = trackRef.current;
    if (!section || !track) return;
    const mm = gsap.matchMedia();
    mm.add("(min-width:1024px)", () => {
      const st = buildReelCinema({
        section,
        track,
        cards: cardsRef.current,
        onProgress: (idx, prog) => {
          setActive(idx);
          if (countRef.current) countRef.current.textContent = String(idx + 1).padStart(2, "0");
          if (fillRef.current) fillRef.current.style.width = `${prog * 100}%`;
        },
      });
      return () => st && st.kill();
    });
    return () => mm.revert();
  }, []);

  useEffect(() => {
    videosRef.current.forEach((v, i) => {
      if (!v) return;
      if (i === active) {
        if (!v.src) v.src = REELS[i].video;
        if (!paused) v.play().catch(() => {});
      } else {
        v.pause();
      }
    });
  }, [active, paused]);

  useEffect(() => {
    videosRef.current.forEach((v) => {
      if (v) v.muted = muted;
    });
  }, [muted]);

  return (
    <section id="showcase" ref={sectionRef}>
      <div className="reel-stage">
        <div className="reel-head">
          <h2>
            {REELCINEMA.headline.replace(REELCINEMA.gold, "")}
            <span className="gold-text">{REELCINEMA.gold}</span>
          </h2>
          <div className="reel-progress">
            <span className="pcount" ref={countRef}>
              01
            </span>
            <div className="ptrack">
              <div className="pfill" ref={fillRef} />
            </div>
          </div>
        </div>

        <div className="reel-track" ref={trackRef}>
          {REELS.map((r, i) => (
            <article
              key={i}
              className={`reel-card ${i === active ? "active" : ""}`}
              ref={(el) => {
                if (el) cardsRef.current[i] = el;
              }}
            >
              <video
                ref={(el) => {
                  videosRef.current[i] = el;
                }}
                muted
                loop
                playsInline
                preload="none"
              />
              <div className="veil" />
              <div className="top">
                <span className="num">
                  {String(i + 1).padStart(2, "0")} / {String(REELS.length).padStart(2, "0")}
                </span>
                <span className="live">
                  <i /> Now Playing
                </span>
              </div>
              <div className="meta">
                <span className="ind">{r.industry}</span>
                <h3 className="ttl">{r.title}</h3>
                <p className="out">{r.outcome}</p>
              </div>
            </article>
          ))}
        </div>

        <div className="reel-floor" />
        <div className="reel-hint" aria-hidden>
          Scroll — Reel Cinema
        </div>
        <div className="reel-controls">
          <button onClick={() => setPaused((p) => !p)} aria-label="Play/Pause">
            {paused ? <Play size={17} /> : <Pause size={17} />}
          </button>
          <button onClick={() => setMuted((m) => !m)} aria-label="Ton an/aus">
            {muted ? <VolumeX size={17} /> : <Volume2 size={17} />}
          </button>
        </div>
      </div>
    </section>
  );
}
