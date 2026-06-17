import { useEffect, useRef, useState } from "react";
import gsap from "gsap";
import { preloader } from "../../content/siteContent";

interface Props {
  onComplete: () => void;
}

/** Premium boot loader: status lines + gold progress, then a curtain exit. */
export default function Preloader({ onComplete }: Props) {
  const root = useRef<HTMLDivElement>(null);
  const bar = useRef<HTMLElement>(null);
  const [pct, setPct] = useState(0);
  const [line, setLine] = useState(0);

  useEffect(() => {
    const state = { p: 0 };
    const tl = gsap.timeline();

    tl.to(state, {
      p: 1,
      duration: 2.4,
      ease: "power2.inOut",
      onUpdate: () => {
        const v = state.p;
        setPct(Math.round(v * 100));
        setLine(Math.min(preloader.lines.length - 1, Math.floor(v * preloader.lines.length)));
        if (bar.current) gsap.set(bar.current, { scaleX: v });
      },
    })
      .to({}, { duration: 0.25 })
      .to(root.current, {
        yPercent: -100,
        duration: 1.1,
        ease: "expo.inOut",
        onComplete,
      });

    return () => {
      tl.kill();
    };
  }, [onComplete]);

  return (
    <div className="preloader" ref={root}>
      <div className="preloader__brand">
        {preloader.brand}
        <small>CONTENT ENGINE · v1.0</small>
      </div>

      <div>
        <div className="preloader__meta">
          <span>{preloader.lines[line]}</span>
          <span className="preloader__pct">{pct}%</span>
        </div>
        <div className="preloader__bar" style={{ marginTop: 14 }}>
          <i ref={bar} style={{ transform: "scaleX(0)" }} />
        </div>
      </div>
    </div>
  );
}
