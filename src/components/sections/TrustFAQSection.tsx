import { useRef, useState } from "react";
import { TRUST, FAQ } from "../../content/siteContent";
import { KineticLabel } from "../ui/KineticLabel";
import { SplitHeadline } from "../ui/SplitHeadline";
import { useScrollReveal } from "../../motion/useScrollReveal";

export function TrustFAQSection() {
  const ref = useRef<HTMLElement>(null);
  useScrollReveal(ref);
  const [open, setOpen] = useState<number | null>(0);

  return (
    <section id="faq" className="scene" ref={ref}>
      <div className="wrap">
        <div className="faq-grid">
          <div>
            <KineticLabel>Vertrauen &amp; FAQ</KineticLabel>
            <SplitHeadline text="Häufige Fragen." gold="Fragen." className="h-section" />
            <ul className="trust-list">
              {TRUST.map((t) => (
                <li key={t}>
                  <span />
                  {t}
                </li>
              ))}
            </ul>
          </div>

          <div className="faq-list">
            {FAQ.map((f, i) => (
              <div className={`faq-item ${open === i ? "open" : ""}`} key={f.q}>
                <button className="faq-q" onClick={() => setOpen(open === i ? null : i)} aria-expanded={open === i}>
                  {f.q}
                  <span className="faq-arrow">+</span>
                </button>
                <div className="faq-a">
                  <div>
                    <p>{f.a}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
