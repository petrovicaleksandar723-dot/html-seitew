import { Reveal } from "../motion/Reveal";
import { LazyVideo } from "../components/LazyVideo";
import { useReel } from "../components/ReelViewer";
import { SHOWCASE } from "../data/content";

export function Showcase() {
  const open = useReel();
  return (
    <section className="section" id="showcase">
      <div className="wrap">
        <Reveal>
          <div className="sec-head center">
            <span className="eyebrow">Showcase</span>
            <h2 className="h2">So sieht dein Content aus.</h2>
            <p className="sub">Echte Reel-Formate – tippen zum Abspielen mit Ton.</p>
          </div>
        </Reveal>
      </div>
      <div className="rail">
        {SHOWCASE.map((s, i) => (
          <div className="reel-card" key={i}>
            <button className="phone" aria-label="Reel abspielen" onClick={() => open(s.src)}>
              <LazyVideo src={s.src} />
              <span className="reel-tap">▶</span>
            </button>
            <div className="cap">{s.cap}</div>
          </div>
        ))}
      </div>
    </section>
  );
}
