import { useEffect, useRef } from "react";
import { DIAGNOSIS } from "../../content/siteContent";
import { KineticLabel } from "../ui/KineticLabel";
import { SplitHeadline } from "../ui/SplitHeadline";
import { SectionVideoBg } from "../ui/SectionVideoBg";
import { useScrollReveal } from "../../motion/useScrollReveal";
import { gsap, ScrollTrigger } from "../../motion/scrollTriggers";

export function DiagnosisSection() {
  const ref = useRef<HTMLElement>(null);
  useScrollReveal(ref);

  useEffect(() => {
    const scope = ref.current;
    if (!scope) return;
    const ctx = gsap.context(() => {
      ScrollTrigger.create({
        trigger: scope.querySelector(".diag-panel") as HTMLElement,
        start: "top 75%",
        once: true,
        onEnter: () => {
          scope.querySelectorAll<HTMLElement>(".meter").forEach((m, i) => {
            const fill = m.querySelector<HTMLElement>(".meter-fill");
            const v = m.getAttribute("data-fill") || "0";
            window.setTimeout(() => {
              if (fill) {
                fill.style.transition = "width 1.3s cubic-bezier(.16,1,.3,1)";
                fill.style.width = `${v}%`;
              }
            }, i * 160);
          });
        },
      });
    }, scope);
    return () => ctx.revert();
  }, []);

  return (
    <section id="problem" className="scene" ref={ref}>
      <SectionVideoBg src="/assets/videos/show-2.mp4" opacity={0.08} />
      <div className="wrap">
        <div className="diag-grid">
          <div className="diag-left">
            <KineticLabel>{DIAGNOSIS.label}</KineticLabel>
            <SplitHeadline className="h-section" text={DIAGNOSIS.headline} gold={DIAGNOSIS.gold} />
            <p className="lede" data-fade>
              {DIAGNOSIS.lede}
            </p>
            <div className="diag-modules">
              {DIAGNOSIS.modules.map((m) => (
                <div className="diag-mod reveal" key={m.k}>
                  <span className="ix">{m.k}</span>
                  <div>
                    <h4>{m.title}</h4>
                    <p>{m.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="diag-panel reveal">
            <div className="diag-panel-head">
              <span className="lbl">Content-Audit · Live-Scan</span>
              <span className="dot" />
            </div>
            {DIAGNOSIS.meters.map((m) => (
              <div className={`meter ${m.tone}`} data-fill={String(m.value)} key={m.label}>
                <div className="meter-top">
                  <span>{m.label}</span>
                  <b>{m.display}</b>
                </div>
                <div className="meter-track">
                  <div className="meter-fill" />
                </div>
              </div>
            ))}
            <div className="diag-status">
              <span className="p" /> {DIAGNOSIS.status}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
