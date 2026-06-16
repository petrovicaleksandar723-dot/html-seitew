import { useRef, useState } from "react";
import { INDUSTRIES } from "../../content/siteContent";
import { KineticLabel } from "../ui/KineticLabel";
import { SplitHeadline } from "../ui/SplitHeadline";
import { SectionNumber } from "../ui/SectionNumber";
import { useScrollReveal } from "../../motion/useScrollReveal";

export function IndustriesSection() {
  const ref = useRef<HTMLElement>(null);
  useScrollReveal(ref);
  const [active, setActive] = useState(INDUSTRIES[0].id);

  return (
    <section id="industries" className="scene" ref={ref}>
      <div className="wrap">
        <div className="sol-head">
          <SectionNumber n="04" />
          <div>
            <KineticLabel>Branchen</KineticLabel>
            <SplitHeadline text="Für Betriebe, die auffallen wollen." gold="auffallen wollen." />
          </div>
        </div>

        <div className="gal">
          <div className="gal-list">
            {INDUSTRIES.map((it, i) => (
              <div
                key={it.id}
                className={`gal-item ${active === it.id ? "active" : ""}`}
                onMouseEnter={() => setActive(it.id)}
                onClick={() => setActive(it.id)}
              >
                <span className="gi-num">{String(i + 1).padStart(2, "0")}</span>
                <span className="gi-name">{it.name}</span>
                <span className="gi-tag">{it.tag}</span>
              </div>
            ))}
          </div>

          <div className="gal-stage">
            {INDUSTRIES.map((it) => (
              <div
                key={it.id}
                className={`gal-vis ${active === it.id ? "active" : ""}`}
                style={{ background: `radial-gradient(120% 120% at 35% 25%, ${it.hue}, #0a0805)` }}
              >
                <div className="mesh" />
                <div className="glow" />
                <div className="vtxt">
                  <span className="vt-k">{it.name}</span>
                  <h4>{it.title}</h4>
                  <p>{it.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
