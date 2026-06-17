import { useEffect, useRef, useState, type CSSProperties } from "react";
import { industries } from "../../content/siteContent";
import SectionNumber from "../ui/SectionNumber";
import SplitHeadline from "../ui/SplitHeadline";
import { gsap } from "../../motion/scrollTriggers";

/** Scene 6 — Industries Editorial Gallery. Type list ↔ large visual stage. */
export default function IndustriesSection() {
  const root = useRef<HTMLElement>(null);
  const videos = useRef<(HTMLVideoElement | null)[]>([]);
  const [active, setActive] = useState(0);

  useEffect(() => {
    videos.current.forEach((v, i) => {
      if (!v) return;
      if (i === active) {
        if (!v.src) v.src = industries.items[i].video;
        v.play().catch(() => {});
      } else {
        v.pause();
      }
    });
  }, [active]);

  useEffect(() => {
    const el = root.current;
    if (!el) return;
    const ctx = gsap.context(() => {
      gsap.from(el.querySelectorAll(".ind-item"), {
        x: -40,
        opacity: 0,
        duration: 0.8,
        stagger: 0.06,
        ease: "power3.out",
        scrollTrigger: { trigger: el, start: "top 65%" },
      });
      gsap.from(el.querySelector(".ind-visual"), {
        scale: 0.92,
        opacity: 0,
        duration: 1.2,
        ease: "expo.out",
        scrollTrigger: { trigger: el, start: "top 70%" },
      });
    }, el);
    return () => ctx.revert();
  }, []);

  const current = industries.items[active];

  return (
    <section className="industries section scene-pad" id="industries" ref={root}>
      <div className="shell">
        <div className="scene-head">
          <SectionNumber num="04" label="Branchen" />
          <div className="eyebrow">{industries.eyebrow}</div>
          <SplitHeadline text={industries.headline} />
          <p className="text-soft">{industries.subline}</p>
        </div>

        <div className="ind-stage">
          <div className="ind-list">
            {industries.items.map((ind, i) => (
              <button
                key={ind.name}
                className={`ind-item ${i === active ? "is-active" : ""}`}
                onMouseEnter={() => setActive(i)}
                onClick={() => setActive(i)}
                data-cursor="hover"
              >
                {ind.name}
              </button>
            ))}
          </div>

          <div>
            <div className="ind-visual" data-parallax="6" style={{ "--glow": current.glow } as CSSProperties}>
              {industries.items.map((ind, i) => (
                <video
                  key={ind.name}
                  ref={(el) => {
                    videos.current[i] = el;
                  }}
                  className={i === active ? "is-active" : ""}
                  muted
                  loop
                  playsInline
                  preload="none"
                  {...(i === 0 ? { src: ind.video } : {})}
                />
              ))}
              <div
                className="ind-visual__glow"
                style={{ background: `radial-gradient(60% 60% at 50% 40%, ${current.glow}, transparent 70%)` }}
              />
              <div className="ind-visual__scrim" />
              <div className="ind-visual__badges">
                <span>Reel Hook</span>
                <span>Caption</span>
                <span>Google Post</span>
                <span>Review Reply</span>
              </div>
              <div className="ind-visual__meta">
                <div className="ind-visual__metric">{current.metric}</div>
                <div className="ind-visual__claim">{current.cta}</div>
              </div>
            </div>

            <div className="ind-readout">
              <div className="row">
                <div className="k">Reel-Idee</div>
                <div className="v">{current.reel}</div>
              </div>
              <div className="row">
                <div className="k">Caption</div>
                <div className="v">{current.caption}</div>
              </div>
              <div className="row">
                <div className="k">Google-Beitrag</div>
                <div className="v">{current.google}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
