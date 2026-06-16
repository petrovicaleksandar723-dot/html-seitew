import { Reveal } from "../motion/Reveal";
import { Icon } from "../components/Icon";
import { SERVICES } from "../data/content";

export function Solution() {
  return (
    <section className="section" id="leistungen">
      <div className="wrap">
        <Reveal>
          <div className="sec-head center">
            <span className="eyebrow">Die Lösung</span>
            <h2 className="h2">Ein komplettes Content-System – fertig für dich.</h2>
            <p className="sub">Du machst dein Geschäft. Wir machen den Content, der dich verkauft – cinematisch, konsistent und planbar.</p>
          </div>
        </Reveal>
        <Reveal stagger>
          <div className="grid g4">
            {SERVICES.map((s) => (
              <div className="card" key={s.t}>
                <div className="ic">
                  <Icon name={s.ic} />
                </div>
                <h3>{s.t}</h3>
                <p>{s.p}</p>
              </div>
            ))}
          </div>
        </Reveal>
      </div>
    </section>
  );
}
