import { useEffect, useRef } from "react";
import { pipeline } from "../../content/siteContent";
import SectionNumber from "../ui/SectionNumber";
import SplitHeadline from "../ui/SplitHeadline";
import { buildPipeline } from "../../motion/pipelineTimeline";
import { gsap } from "../../motion/scrollTriggers";

/** Scene 8 — Production Pipeline. Gold signal travels the rail, lighting steps. */
export default function PipelineSection() {
  const root = useRef<HTMLElement>(null);
  const rail = useRef<HTMLElement>(null);
  const signal = useRef<HTMLDivElement>(null);
  const steps = useRef<(HTMLDivElement | null)[]>([]);

  useEffect(() => {
    const el = root.current;
    const r = rail.current;
    const s = signal.current;
    if (!el || !r || !s) return;
    const ctx = gsap.context(() => {
      const stepEls = steps.current.filter(Boolean) as HTMLElement[];
      gsap.set(r, { scaleX: 0, transformOrigin: "left" });
      buildPipeline(el, r, s, stepEls);
    }, el);
    return () => ctx.revert();
  }, []);

  return (
    <section className="pipeline section scene-pad" id="pipeline" ref={root}>
      <div className="shell">
        <div className="scene-head">
          <SectionNumber num="05" label="Pipeline" />
          <div className="eyebrow">{pipeline.eyebrow}</div>
          <SplitHeadline text={pipeline.headline} />
          <p className="text-soft">{pipeline.subline}</p>
        </div>

        <div className="pipe-track">
          <div className="pipe-rail">
            <i ref={rail} />
          </div>
          <div className="pipe-signal" ref={signal} />
          {pipeline.steps.map((step, i) => (
            <div
              key={step.num}
              className="pipe-step"
              ref={(el) => {
                steps.current[i] = el;
              }}
            >
              <div className="pipe-node" />
              <div className="pipe-num">{step.num}</div>
              <h3 className="pipe-title">{step.title}</h3>
              <p className="pipe-body">{step.body}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
