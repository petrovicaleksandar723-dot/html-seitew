import { useEffect, useRef } from "react";
import { TRANSFORMATION as T } from "../../content/siteContent";
import { VideoPanel } from "../ui/VideoPanel";
import { buildTransformation } from "../../motion/transformationTimeline";
import { gsap } from "../../motion/scrollTriggers";

export function TransformationSection() {
  const sectionRef = useRef<HTMLElement>(null);
  const afterRef = useRef<HTMLDivElement>(null);
  const dividerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const section = sectionRef.current;
    const after = afterRef.current;
    const divider = dividerRef.current;
    if (!section || !after || !divider) return;

    const mm = gsap.matchMedia();
    mm.add("(min-width:1024px)", () => {
      const tl = buildTransformation({ section, after, divider });
      return () => tl.scrollTrigger?.kill();
    });
    mm.add("(max-width:1023px)", () => {
      after.style.clipPath = "none";
      divider.style.display = "none";
    });
    return () => mm.revert();
  }, []);

  return (
    <section id="transform" ref={sectionRef}>
      <div className="ba-stage">
        <div className="ba-layer ba-before">
          <div className="ba-content">
            <span className="ba-state">{T.before.state}</span>
            <h2 className="ba-h">{T.before.headline}</h2>
            <ul className="ba-list">
              {T.before.list.map((l) => (
                <li key={l}>{l}</li>
              ))}
            </ul>
          </div>
        </div>
        <div className="ba-layer ba-after" ref={afterRef}>
          <VideoPanel src={T.after.video} className="ba-video" />
          <div className="ba-content">
            <span className="ba-state">{T.after.state}</span>
            <h2 className="ba-h">
              Ein Auftritt, der <span className="gold-text">Vertrauen verkauft.</span>
            </h2>
            <ul className="ba-list">
              {T.after.list.map((l) => (
                <li key={l}>{l}</li>
              ))}
            </ul>
          </div>
        </div>
        <div className="ba-divider" ref={dividerRef} />
      </div>
    </section>
  );
}
