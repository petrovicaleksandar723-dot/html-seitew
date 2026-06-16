import { useEffect, useRef } from "react";

/** Magnetic hover: element gently pulls toward the cursor (desktop fine-pointer only). */
export function useMagnetic<T extends HTMLElement>(strength = 0.35) {
  const ref = useRef<T>(null);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    if (!window.matchMedia("(hover:hover) and (pointer:fine)").matches) return;
    const move = (e: PointerEvent) => {
      const r = el.getBoundingClientRect();
      const x = (e.clientX - r.left - r.width / 2) * strength;
      const y = (e.clientY - r.top - r.height / 2) * strength;
      el.style.transform = `translate(${x.toFixed(1)}px, ${y.toFixed(1)}px)`;
    };
    const leave = () => {
      el.style.transform = "";
    };
    el.addEventListener("pointermove", move);
    el.addEventListener("pointerleave", leave);
    return () => {
      el.removeEventListener("pointermove", move);
      el.removeEventListener("pointerleave", leave);
    };
  }, [strength]);
  return ref;
}
