import { useEffect, useState } from "react";
import { PRELOADER_LINES } from "../../content/siteContent";

export function Preloader() {
  const [done, setDone] = useState(false);
  const [hidden, setHidden] = useState(false);
  const [pct, setPct] = useState(0);
  const [line, setLine] = useState(0);

  useEffect(() => {
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const DUR = reduce ? 250 : 1900;
    let raf = 0;
    let start = 0;
    let finished = false;
    const finish = () => {
      if (finished) return;
      finished = true;
      setDone(true);
      window.setTimeout(() => setHidden(true), 1000);
    };
    const tick = (ts: number) => {
      if (!start) start = ts;
      const t = Math.min((ts - start) / DUR, 1);
      setPct(Math.round(t * 100));
      setLine(Math.min(PRELOADER_LINES.length - 1, Math.floor(t * PRELOADER_LINES.length)));
      if (t < 1) raf = requestAnimationFrame(tick);
      else window.setTimeout(finish, 250);
    };
    raf = requestAnimationFrame(tick);
    const safety = window.setTimeout(finish, 4500);
    return () => {
      cancelAnimationFrame(raf);
      clearTimeout(safety);
    };
  }, []);

  if (hidden) return null;
  return (
    <div className={`preloader ${done ? "done" : ""}`}>
      <div className="pl-logo">
        CleanLines<span className="gold-text">.</span>
        <small>STUDIO</small>
      </div>
      <div className="pl-sub">{PRELOADER_LINES[line]}</div>
      <div className="pl-bar">
        <i style={{ width: `${pct}%` }} />
      </div>
      <div className="pl-count">{pct}%</div>
    </div>
  );
}
