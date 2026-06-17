import { useEffect, useRef } from "react";
import { diagnosis } from "../../content/siteContent";
import SectionNumber from "../ui/SectionNumber";
import SplitHeadline from "../ui/SplitHeadline";
import { gsap, ScrollTrigger } from "../../motion/scrollTriggers";

/** Scene 3 — Diagnosis Dashboard. Cinematic diagnostic panels + meters. */
export default function DiagnosisSection() {
  const root = useRef<HTMLElement>(null);

  useEffect(() => {
    const el = root.current;
    if (!el) return;
    const ctx = gsap.context(() => {
      const panel = el.querySelector(".diag-panel");
      if (panel) {
        gsap.from(panel, {
          y: 80,
          opacity: 0,
          rotateX: 8,
          duration: 1.2,
          ease: "expo.out",
          scrollTrigger: { trigger: panel, start: "top 82%" },
        });
      }
      // meters animate from 0
      el.querySelectorAll<HTMLElement>(".meter__fill").forEach((fill) => {
        const target = fill.dataset.value ?? "0";
        gsap.to(fill, {
          width: `${target}%`,
          duration: 1.6,
          ease: "power3.out",
          scrollTrigger: { trigger: el, start: "top 60%" },
        });
      });
      gsap.from(el.querySelectorAll(".diag-readouts span"), {
        y: 20,
        opacity: 0,
        duration: 0.7,
        stagger: 0.08,
        ease: "power3.out",
        scrollTrigger: { trigger: el, start: "top 55%" },
      });
      ScrollTrigger.refresh();
    }, el);
    return () => ctx.revert();
  }, []);

  return (
    <section className="diagnosis section scene-pad" id="diagnosis" ref={root}>
      <div className="shell">
        <div className="diag-grid">
          <div className="scene-head">
            <SectionNumber num="01" label="Diagnose" />
            <div className="eyebrow">{diagnosis.eyebrow}</div>
            <SplitHeadline text={diagnosis.headline} />
            <p className="text-soft">{diagnosis.subline}</p>
          </div>

          <div className="diag-panel">
            <div className="diag-scanline" />
            {diagnosis.meters.map((m) => (
              <div className="meter" key={m.label}>
                <div className="meter__top">
                  <span className="meter__label">{m.label}</span>
                  <span className="meter__state">{m.state}</span>
                </div>
                <div className="meter__bar">
                  <div className="meter__fill" data-value={m.value} />
                </div>
              </div>
            ))}
            <div className="diag-readouts">
              {diagnosis.readouts.map((r) => (
                <span key={r}>{r}</span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
