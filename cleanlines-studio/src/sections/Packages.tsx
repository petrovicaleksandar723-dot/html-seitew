import { Reveal } from "../motion/Reveal";
import { Icon } from "../components/Icon";
import { PACKAGES, MAIL } from "../data/content";

export function Packages() {
  return (
    <section className="section" id="pakete">
      <div className="wrap">
        <Reveal>
          <div className="sec-head center">
            <span className="eyebrow">Pakete</span>
            <h2 className="h2">Wähle, wie sichtbar du werden willst.</h2>
          </div>
        </Reveal>
        <Reveal stagger>
          <div className="plans">
            {PACKAGES.map((p) => (
              <article className={"plan" + (p.feat ? " feat" : "")} key={p.name}>
                {p.feat && <span className="badge">Beliebt</span>}
                <div className="pn">{p.name}</div>
                <div className="pr">
                  <b>{p.price}</b>
                  <span>/Monat</span>
                </div>
                <p className="pd">{p.desc}</p>
                <ul>
                  {p.items.map((it) => (
                    <li key={it}>
                      <Icon name="check" />
                      {it}
                    </li>
                  ))}
                </ul>
                <a className="pc" href={MAIL}>
                  {p.name} anfragen
                </a>
              </article>
            ))}
          </div>
        </Reveal>
        <Reveal>
          <p className="note">
            Cinematische Reel-Produktion ist in jedem Paket enthalten. Keine direkte Zahlung auf der Website – du bekommst zuerst eine kurze Einschätzung, welches Paket zu deinem Betrieb passt.
          </p>
        </Reveal>
      </div>
    </section>
  );
}
