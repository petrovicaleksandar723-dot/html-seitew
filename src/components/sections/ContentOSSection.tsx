import { useEffect, useMemo, useRef } from "react";
import { contentOS } from "../../content/siteContent";
import SectionNumber from "../ui/SectionNumber";
import SplitHeadline from "../ui/SplitHeadline";
import { gsap } from "../../motion/scrollTriggers";

/** Scene 4 — Content Operating System. Central core + modules on connections. */
export default function ContentOSSection() {
  const root = useRef<HTMLElement>(null);

  // distribute modules on an ellipse around the core
  const placed = useMemo(() => {
    const n = contentOS.modules.length;
    return contentOS.modules.map((label, i) => {
      const angle = (i / n) * Math.PI * 2 - Math.PI / 2;
      const rx = 38; // % radius x
      const ry = 40; // % radius y
      return {
        label,
        left: 50 + Math.cos(angle) * rx,
        top: 50 + Math.sin(angle) * ry,
      };
    });
  }, []);

  useEffect(() => {
    const el = root.current;
    if (!el) return;
    const ctx = gsap.context(() => {
      const modules = el.querySelectorAll<HTMLElement>(".os-module");
      gsap.from(modules, {
        scale: 0.4,
        opacity: 0,
        duration: 0.8,
        ease: "back.out(1.7)",
        stagger: 0.09,
        scrollTrigger: { trigger: el, start: "top 60%" },
      });
      modules.forEach((mod, i) => {
        gsap.to(mod, {
          duration: 0.01,
          scrollTrigger: {
            trigger: el,
            start: `top ${55 - i * 2}%`,
            onEnter: () => mod.classList.add("is-on"),
          },
        });
      });
      gsap.from(el.querySelector(".os-core"), {
        scale: 0.6,
        opacity: 0,
        duration: 1,
        ease: "expo.out",
        scrollTrigger: { trigger: el, start: "top 65%" },
      });
    }, el);
    return () => ctx.revert();
  }, []);

  return (
    <section className="os section scene-pad" id="content-os" ref={root}>
      <div className="shell">
        <div className="scene-head">
          <SectionNumber num="02" label="System" />
          <div className="eyebrow">{contentOS.eyebrow}</div>
          <SplitHeadline text={contentOS.headline} />
        </div>

        <div className="os-stage">
          <svg className="os-svg" viewBox="0 0 100 100" preserveAspectRatio="none">
            {placed.map((p) => (
              <line key={p.label} className="os-link" x1="50" y1="50" x2={p.left} y2={p.top} />
            ))}
          </svg>

          <div className="os-core">
            <div>
              <span>POWERED BY</span>
              <b>{contentOS.core}</b>
            </div>
          </div>

          {placed.map((p) => (
            <div
              key={p.label}
              className="os-module"
              style={{ left: `${p.left}%`, top: `${p.top}%` }}
            >
              <span className="od" />
              {p.label}
            </div>
          ))}
        </div>

        <p className="os-body">
          Du bekommst nicht einfach ein Video. Du bekommst{" "}
          <b>ein wiederholbares Content-System, das deinen Betrieb regelmäßig sichtbar macht</b> —
          geplant in Themen, Formaten und Posting-Ideen, damit dein Auftritt wie eine klare Marke wirkt.
        </p>
      </div>
    </section>
  );
}
