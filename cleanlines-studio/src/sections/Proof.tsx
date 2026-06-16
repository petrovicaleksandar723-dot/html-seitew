import { Reveal } from "../motion/Reveal";
import { REVIEWS } from "../data/content";

export function Proof() {
  return (
    <section className="section" id="stimmen">
      <div className="wrap">
        <Reveal>
          <div className="sec-head center">
            <span className="eyebrow">Stimmen</span>
            <h2 className="h2">Betriebe, die sich nicht mehr verstecken.</h2>
          </div>
        </Reveal>
        <Reveal stagger>
          <div className="reviews">
            {REVIEWS.map((r) => (
              <div className="review" key={r.who}>
                <div className="stars">{r.stars}</div>
                <p>{r.p}</p>
                <div className="who">
                  <span className="ava">{r.ava}</span>
                  {r.who} · {r.role}
                </div>
              </div>
            ))}
          </div>
        </Reveal>
      </div>
    </section>
  );
}
