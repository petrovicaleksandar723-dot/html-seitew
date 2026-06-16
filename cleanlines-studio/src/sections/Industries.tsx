import { Reveal } from "../motion/Reveal";
import { INDUSTRIES, INDUSTRY_TAGS } from "../data/content";

export function Industries() {
  return (
    <section className="section" id="branchen">
      <div className="wrap">
        <Reveal>
          <div className="sec-head center">
            <span className="eyebrow">Für wen</span>
            <h2 className="h2">Für lokale Betriebe, die auffallen wollen.</h2>
            <p className="sub">Vom Restaurant bis zur Praxis – sichtbar wird, wer regelmäßig hochwertigen Content zeigt.</p>
          </div>
        </Reveal>
      </div>
      <div className="rail">
        {INDUSTRIES.map((x) => (
          <div className="scard" key={x.t}>
            <img loading="lazy" alt={x.t} src={x.img} />
            <div className="sc-s" />
            <div className="sc-b">
              <span className="m">{x.m}</span>
              <h3>{x.t}</h3>
            </div>
          </div>
        ))}
      </div>
      <div className="wrap">
        <Reveal>
          <div className="pills">
            {INDUSTRY_TAGS.map((t) => (
              <span className="pill" key={t}>
                {t}
              </span>
            ))}
          </div>
        </Reveal>
      </div>
    </section>
  );
}
