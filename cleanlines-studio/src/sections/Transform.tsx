import { Reveal } from "../motion/Reveal";
import { Button } from "../components/Button";
import { MAIL } from "../data/content";

const BEFORE = ["Handyfotos ohne Linie", "Posts entstehen spontan oder gar nicht", "Google-Profil bleibt leer", "Wirkt beliebig und austauschbar", "Kunden gehen zur Konkurrenz"];
const AFTER = ["Cinematische Reels mit klarer Handschrift", "Jeden Monat fertiger Content", "Aktives, gepflegtes Google-Profil", "Premium-Auftritt, der Vertrauen schafft", "Mehr Anfragen und Buchungen"];

export function Transform() {
  return (
    <section className="section" id="vorher-nachher">
      <div className="wrap">
        <Reveal>
          <div className="sec-head center">
            <span className="eyebrow">Vorher / Nachher</span>
            <h2 className="h2">Vom unsichtbaren Betrieb zur Premium-Marke.</h2>
          </div>
        </Reveal>
        <div className="ba">
          <Reveal>
            <div className="col before">
              <h4>Vorher</h4>
              <ul>
                {BEFORE.map((x) => (
                  <li key={x}>{x}</li>
                ))}
              </ul>
            </div>
          </Reveal>
          <Reveal delay={0.1}>
            <div className="col after">
              <h4>Nachher</h4>
              <ul>
                {AFTER.map((x) => (
                  <li key={x}>{x}</li>
                ))}
              </ul>
            </div>
          </Reveal>
        </div>
        <Reveal>
          <div className="btns center" style={{ marginTop: 32 }}>
            <Button href={MAIL}>Meinen Auftritt aufwerten</Button>
          </div>
        </Reveal>
      </div>
    </section>
  );
}
