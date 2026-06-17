import { useEffect, useRef, useState } from "react";
import { trust, faq } from "../../content/siteContent";
import SectionNumber from "../ui/SectionNumber";
import SplitHeadline from "../ui/SplitHeadline";
import { gsap } from "../../motion/scrollTriggers";

/** Scene 11 — Trust + FAQ. Trust protocol + premium accordion. */
export default function TrustFAQSection() {
  const root = useRef<HTMLElement>(null);
  const [open, setOpen] = useState<number>(0);
  const answers = useRef<(HTMLDivElement | null)[]>([]);

  useEffect(() => {
    const el = root.current;
    if (!el) return;
    const ctx = gsap.context(() => {
      gsap.from(el.querySelectorAll(".trust-card"), {
        x: -40,
        opacity: 0,
        duration: 0.9,
        stagger: 0.1,
        ease: "power3.out",
        scrollTrigger: { trigger: el, start: "top 70%" },
      });
      gsap.from(el.querySelectorAll(".faq-item"), {
        y: 36,
        opacity: 0,
        duration: 0.8,
        stagger: 0.08,
        ease: "power3.out",
        scrollTrigger: { trigger: el, start: "top 68%" },
      });
    }, el);
    return () => ctx.revert();
  }, []);

  const toggle = (i: number) => {
    const next = open === i ? -1 : i;
    // animate the outgoing + incoming
    [open, next].forEach((idx) => {
      const el = answers.current[idx];
      if (!el) return;
      const isOpening = idx === next && next !== -1;
      gsap.to(el, {
        height: isOpening ? el.scrollHeight : 0,
        duration: 0.6,
        ease: "expo.out",
      });
    });
    setOpen(next);
  };

  return (
    <section className="trustfaq section scene-pad" id="trust-faq" ref={root}>
      <div className="shell">
        <div className="scene-head">
          <SectionNumber num="08" label="Trust & FAQ" />
          <div className="eyebrow">{trust.eyebrow}</div>
          <SplitHeadline text={trust.headline} />
        </div>

        <div className="tf-grid">
          <div className="trust-list">
            {trust.protocol.map((t) => (
              <div className="trust-card" key={t.title}>
                <h4>{t.title}</h4>
                <p>{t.body}</p>
              </div>
            ))}
          </div>

          <div className="faq-list">
            {faq.items.map((item, i) => (
              <div className={`faq-item ${open === i ? "is-open" : ""}`} key={item.q}>
                <button className="faq-q" onClick={() => toggle(i)} data-cursor="hover">
                  {item.q}
                  <span className="faq-icon" />
                </button>
                <div
                  className="faq-a"
                  ref={(el) => {
                    answers.current[i] = el;
                  }}
                  style={{ height: open === i ? "auto" : 0 }}
                >
                  <div className="faq-a__inner">{item.a}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
