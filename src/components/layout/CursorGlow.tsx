import { useEffect, useRef } from "react";

export function CursorGlow() {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!window.matchMedia("(pointer:fine) and (min-width:1024px)").matches) return;
    const el = ref.current;
    if (!el) return;
    const move = (e: MouseEvent) => {
      el.style.opacity = "1";
      el.style.transform = `translate(${e.clientX}px,${e.clientY}px)`;
    };
    const leave = () => {
      el.style.opacity = "0";
    };
    window.addEventListener("mousemove", move);
    document.addEventListener("mouseleave", leave);
    return () => {
      window.removeEventListener("mousemove", move);
      document.removeEventListener("mouseleave", leave);
    };
  }, []);
  return <div ref={ref} className="cursor-glow" aria-hidden />;
}
