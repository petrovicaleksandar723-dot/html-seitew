import { useRef } from "react";
import { Film, Sparkles, Globe, PenLine, CalendarDays, Star, Send, LayoutGrid, Cpu } from "lucide-react";
import { OS } from "../../content/siteContent";
import { KineticLabel } from "../ui/KineticLabel";
import { SplitHeadline } from "../ui/SplitHeadline";
import { SectionNumber } from "../ui/SectionNumber";
import { useScrollReveal } from "../../motion/useScrollReveal";

const ICONS = [Film, Sparkles, Globe, PenLine, CalendarDays, Star, Send, LayoutGrid];

export function ContentOSSection() {
  const ref = useRef<HTMLElement>(null);
  useScrollReveal(ref);

  return (
    <section id="system" className="scene" ref={ref}>
      <div className="wrap">
        <div className="sol-head">
          <SectionNumber n="02" />
          <div>
            <KineticLabel>{OS.label}</KineticLabel>
            <SplitHeadline text={OS.headline} gold={OS.gold} />
          </div>
        </div>
        <p className="lede" data-fade style={{ margin: "-30px 0 56px" }}>
          {OS.lede}
        </p>

        <div className="os">
          {OS.modules.map((m, i) => {
            const Icon = ICONS[i % ICONS.length];
            return (
              <div className="os-mod reveal" key={m.n}>
                <span className="mnum">{m.n}</span>
                <Icon className="ic" strokeWidth={1.5} />
                <h4>{m.title}</h4>
                <p>{m.desc}</p>
              </div>
            );
          })}

          <div className="os-core reveal" style={{ gridColumn: 2, gridRow: 1 }}>
            <span className="ring" aria-hidden />
            <span className="glyph">
              <Cpu size={26} strokeWidth={1.8} />
            </span>
            <h3>{OS.core.title}</h3>
            <p>{OS.core.desc}</p>
          </div>
        </div>
      </div>
    </section>
  );
}
