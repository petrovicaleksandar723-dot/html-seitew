import { Reveal } from "../motion/Reveal";
import { PROBLEMS } from "../data/content";

export function Problem() {
  return (
    <section className="section" id="problem">
      <div className="wrap">
        <Reveal>
          <div className="sec-head center">
            <span className="eyebrow">Das Problem</span>
            <h2 className="h2">Dein Betrieb ist top. Online sieht das niemand.</h2>
            <p className="sub">Lokale Betriebe verlieren jeden Tag Kunden – nicht wegen der Leistung, sondern weil online der Auftritt fehlt.</p>
          </div>
        </Reveal>
        <Reveal stagger>
          <div className="grid g3">
            {PROBLEMS.map((x) => (
              <div className="card" key={x.t}>
                <h3>{x.t}</h3>
                <p>{x.p}</p>
              </div>
            ))}
          </div>
        </Reveal>
      </div>
    </section>
  );
}
