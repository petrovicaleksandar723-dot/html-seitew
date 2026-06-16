import { Reveal } from "../motion/Reveal";
import { PROCESS } from "../data/content";

export function Process() {
  return (
    <section className="section" id="ablauf">
      <div className="wrap">
        <Reveal>
          <div className="sec-head center">
            <span className="eyebrow">So arbeiten wir</span>
            <h2 className="h2">Von der Idee zum fertigen Content.</h2>
            <p className="sub">Ein klarer Ablauf statt Agentur-Chaos – du bist in wenigen Schritten sichtbar.</p>
          </div>
        </Reveal>
        <Reveal stagger>
          <div className="grid g4">
            {PROCESS.map((p, i) => (
              <div className="card" key={p.t}>
                <span className="step-n">{String(i + 1).padStart(2, "0")}</span>
                <div className="ic">
                  <b>{i + 1}</b>
                </div>
                <h3>{p.t}</h3>
                <p>{p.p}</p>
              </div>
            ))}
          </div>
        </Reveal>
      </div>
    </section>
  );
}
