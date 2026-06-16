import { useState } from "react";
import { Reveal } from "../motion/Reveal";
import { FAQS } from "../data/content";

export function Faq() {
  const [open, setOpen] = useState(0);
  return (
    <section className="section" id="faq">
      <div className="wrap">
        <Reveal>
          <div className="sec-head center">
            <span className="eyebrow">FAQ</span>
            <h2 className="h2">Häufige Fragen.</h2>
          </div>
        </Reveal>
        <Reveal>
          <div className="faq">
            {FAQS.map((f, i) => (
              <div className={"faq-item" + (open === i ? " open" : "")} key={i}>
                <button className="faq-q" aria-expanded={open === i} onClick={() => setOpen(open === i ? -1 : i)}>
                  {f.q}
                  <span className="faq-pm" />
                </button>
                <div className="faq-a">
                  <p>{f.a}</p>
                </div>
              </div>
            ))}
          </div>
        </Reveal>
      </div>
    </section>
  );
}
