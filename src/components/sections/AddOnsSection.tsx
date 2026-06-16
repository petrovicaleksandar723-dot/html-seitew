import { useRef } from "react";
import { Monitor, Palette, Clapperboard, Share2 } from "lucide-react";
import { ADDONS } from "../../content/siteContent";
import { KineticLabel } from "../ui/KineticLabel";
import { SplitHeadline } from "../ui/SplitHeadline";
import { SectionNumber } from "../ui/SectionNumber";
import { useScrollReveal } from "../../motion/useScrollReveal";

const ICONS = [Monitor, Palette, Clapperboard, Share2];

export function AddOnsSection() {
  const ref = useRef<HTMLElement>(null);
  useScrollReveal(ref);

  return (
    <section id="addons" className="scene" ref={ref}>
      <div className="wrap">
        <div className="sol-head">
          <SectionNumber n="08" />
          <div>
            <KineticLabel>Einzelaufträge</KineticLabel>
            <SplitHeadline text="Du brauchst mehr als Content?" gold="mehr als Content?" />
          </div>
        </div>
        <p className="lede" data-fade style={{ margin: "-30px 0 6px" }}>
          Für einzelne Projekte bekommst du klare Festpreise, saubere Umsetzung und ein Ergebnis, das professionell wirkt.
        </p>

        <div className="addons">
          {ADDONS.map((a, i) => {
            const Icon = ICONS[i % ICONS.length];
            return (
              <div className="addon reveal" key={a.title}>
                <div className="addon-ic">
                  <Icon strokeWidth={1.6} />
                </div>
                <div className="addon-body">
                  <h4>{a.title}</h4>
                  <p>{a.desc}</p>
                </div>
                <div className="addon-price">{a.price}</div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
