import { useEffect, useRef } from "react";
import gsap from "gsap";

/** Custom gold cursor: a soft ring that lags the pointer + a precise dot. */
export default function CursorGlow() {
  const ring = useRef<HTMLDivElement>(null);
  const dot = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (window.matchMedia("(pointer: coarse)").matches) return;
    const ringEl = ring.current;
    const dotEl = dot.current;
    if (!ringEl || !dotEl) return;

    const ringX = gsap.quickTo(ringEl, "x", { duration: 0.5, ease: "power3" });
    const ringY = gsap.quickTo(ringEl, "y", { duration: 0.5, ease: "power3" });
    const dotX = gsap.quickTo(dotEl, "x", { duration: 0.12, ease: "power2" });
    const dotY = gsap.quickTo(dotEl, "y", { duration: 0.12, ease: "power2" });

    const move = (e: MouseEvent) => {
      ringX(e.clientX);
      ringY(e.clientY);
      dotX(e.clientX);
      dotY(e.clientY);
    };

    const over = (e: MouseEvent) => {
      const target = (e.target as HTMLElement)?.closest("[data-cursor='hover'], a, button");
      ringEl.classList.toggle("is-active", !!target);
    };

    window.addEventListener("mousemove", move);
    window.addEventListener("mouseover", over);
    return () => {
      window.removeEventListener("mousemove", move);
      window.removeEventListener("mouseover", over);
    };
  }, []);

  return (
    <>
      <div ref={ring} className="cursor-glow" aria-hidden />
      <div ref={dot} className="cursor-dot" aria-hidden />
    </>
  );
}
