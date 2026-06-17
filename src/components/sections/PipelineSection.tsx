import { useEffect, useRef } from "react";
import { Search, Lightbulb, Clapperboard, Send } from "lucide-react";
import { PIPELINE } from "../../content/siteContent";
import { KineticLabel } from "../ui/KineticLabel";
import { SplitHeadline } from "../ui/SplitHeadline";
import { SectionNumber } from "../ui/SectionNumber";
import { SectionVideoBg } from "../ui/SectionVideoBg";
import { useScrollReveal } from "../../motion/useScrollReveal";
import { buildPipeline } from "../../motion/pipelineTimeline";
import { gsap } from "../../motion/scrollTriggers";

const ICONS = [Search, Lightbulb, Clapperboard, Send];

export function PipelineSection() {
  const ref = useRef<HTMLElement>(null);
  const pipeRef = useRef<HTMLDivElement>(null);
  const fillRef = useRef<HTMLDivElement>(null);
  useScrollReveal(ref);

  useEffect(() => {
    const pipe = pipeRef.current;
    const fill = fillRef.current;
    if (!pipe || !fill) return;
    const steps = Array.from(pipe.querySelectorAll<HTMLElement>(".pipe-step"));
    const mm = gsap.matchMedia();
    mm.add("(min-width:1024px)", () => {
      const tw = buildPipeline({ trigger: pipe, fill, steps });
      return () => tw.scrollTrigger?.kill();
    });
    mm.add("(max-width:1023px)", () => {
      steps.forEach((s) => s.classList.add("on"));
    });
    return () => mm.revert();
  }, []);

  return (
    <section id="process" className="scene" ref={ref}>
      <SectionVideoBg src="/assets/videos/show-4.mp4" opacity={0.1} />
      <div className="wrap">
        <div className="sol-head">
          <SectionNumber n="06" />
          <div>
            <KineticLabel>{PIPELINE.label}</KineticLabel>
            <SplitHeadline text={PIPELINE.headline} gold={PIPELINE.gold} />
          </div>
        </div>

        <div className="pipe" ref={pipeRef}>
          <div className="pipe-rail">
            <div className="pfill" ref={fillRef} />
          </div>
          <div className="pipe-steps">
            {PIPELINE.steps.map((s, i) => {
              const Icon = ICONS[i % ICONS.length];
              return (
                <div className="pipe-step" key={s.n}>
                  <div className="pipe-node">
                    <Icon className="ic" strokeWidth={1.5} />
                  </div>
                  <span className="pnum">Schritt {s.n}</span>
                  <h4>{s.title}</h4>
                  <p>{s.desc}</p>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}
