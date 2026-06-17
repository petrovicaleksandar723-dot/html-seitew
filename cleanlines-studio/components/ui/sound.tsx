"use client";

import { useEffect, useRef, useState } from "react";

export function SoundLayer() {
  const [on, setOn] = useState(false);
  const ctxRef = useRef<AudioContext | null>(null);
  const lastHover = useRef(0);
  const lastTarget = useRef<EventTarget | null>(null);

  const tick = (
    freq: number,
    dur: number,
    gain: number,
    type: OscillatorType,
    sweepTo?: number
  ) => {
    const ctx = ctxRef.current;
    if (!ctx) return;
    const now = ctx.currentTime;
    const osc = ctx.createOscillator();
    const g = ctx.createGain();
    osc.type = type;
    osc.frequency.setValueAtTime(freq, now);
    if (sweepTo) osc.frequency.exponentialRampToValueAtTime(sweepTo, now + dur);
    g.gain.setValueAtTime(0, now);
    g.gain.linearRampToValueAtTime(gain, now + 0.005);
    g.gain.exponentialRampToValueAtTime(0.0001, now + dur);
    osc.connect(g).connect(ctx.destination);
    osc.start(now);
    osc.stop(now + dur + 0.02);
  };

  useEffect(() => {
    if (!on) return;

    if (!ctxRef.current) {
      const AC =
        window.AudioContext ||
        (window as unknown as { webkitAudioContext: typeof AudioContext })
          .webkitAudioContext;
      ctxRef.current = new AC();
    }
    ctxRef.current?.resume();

    const hot = "a,button,[data-hot]";
    const onOver = (e: PointerEvent) => {
      const t = (e.target as HTMLElement)?.closest(hot);
      if (!t || t === lastTarget.current) return;
      const now = performance.now();
      if (now - lastHover.current < 60) return;
      lastHover.current = now;
      lastTarget.current = t;
      tick(1180, 0.05, 0.022, "sine");
    };
    const onOut = () => {
      lastTarget.current = null;
    };
    const onClick = (e: MouseEvent) => {
      if (!(e.target as HTMLElement)?.closest(hot)) return;
      tick(540, 0.12, 0.05, "triangle", 180);
    };

    document.addEventListener("pointerover", onOver);
    document.addEventListener("pointerout", onOut);
    document.addEventListener("click", onClick);
    return () => {
      document.removeEventListener("pointerover", onOver);
      document.removeEventListener("pointerout", onOut);
      document.removeEventListener("click", onClick);
    };
  }, [on]);

  return (
    <button
      onClick={() => setOn((v) => !v)}
      aria-label={on ? "Sound aus" : "Sound an"}
      className="fixed bottom-6 left-6 z-[80] flex items-center gap-2.5 rounded-full border border-line bg-bg/70 px-4 py-2.5 backdrop-blur-md transition-colors hover:border-gold/40"
    >
      <span className="flex h-3.5 items-end gap-[2px]">
        {[0, 1, 2, 3].map((i) => (
          <span
            key={i}
            className="w-[2px] rounded-full bg-gold"
            style={{
              height: on ? undefined : "4px",
              animation: on
                ? `eq 0.9s ease-in-out ${i * 0.12}s infinite alternate`
                : "none",
            }}
          />
        ))}
      </span>
      <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-dim">
        {on ? "Sound" : "Stumm"}
      </span>
      <style>{`@keyframes eq{from{height:3px}to{height:14px}}`}</style>
    </button>
  );
}
