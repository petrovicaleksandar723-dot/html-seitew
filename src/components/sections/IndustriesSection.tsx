import { useRef, useState } from "react";
import { INDUSTRIES, INDUSTRIES_HEAD } from "../../content/siteContent";
import { KineticLabel } from "../ui/KineticLabel";
import { SplitHeadline } from "../ui/SplitHeadline";
import { SectionNumber } from "../ui/SectionNumber";
import { useScrollReveal } from "../../motion/useScrollReveal";

export function IndustriesSection() {
  const ref = useRef<HTMLElement>(null);
  useScrollReveal(ref);
  const [activeId, setActiveId] = useState(INDUSTRIES[0].id);
  const active = INDUSTRIES.find((i) => i.id === activeId) ?? INDUSTRIES[0];

  return (
    <section id="industries" className="scene" ref={ref}>
      <div className="wrap">
        <div className="sol-head">
          <SectionNumber n="04" />
          <div>
            <KineticLabel>Branchen</KineticLabel>
            <SplitHeadline text={INDUSTRIES_HEAD.headline} gold={INDUSTRIES_HEAD.gold} />
          </div>
        </div>
        <p className="lede" data-fade style={{ margin: "-30px 0 36px" }}>
          {INDUSTRIES_HEAD.sub}
        </p>

        <div className="gal">
          <div className="gal-list">
            {INDUSTRIES.map((it, i) => (
              <div
                key={it.id}
                className={`gal-item ${activeId === it.id ? "active" : ""}`}
                onMouseEnter={() => setActiveId(it.id)}
                onClick={() => setActiveId(it.id)}
              >
                <span className="gi-num">{String(i + 1).padStart(2, "0")}</span>
                <span className="gi-name">{it.name}</span>
                <span className="gi-tag">{it.tag}</span>
              </div>
            ))}
          </div>

          <div className="gal-stage" style={{ background: `radial-gradient(120% 120% at 35% 25%, ${active.hue}, #0a0805)` }}>
            <video
              className="gal-video"
              key={active.video}
              src={active.video}
              autoPlay
              muted
              loop
              playsInline
              preload="metadata"
            />
            <div className="gal-veil" />
            <div className="gal-vtxt" key={active.id}>
              <span className="vt-k">{active.name}</span>
              <h4>{active.title}</h4>
              <p>{active.desc}</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
