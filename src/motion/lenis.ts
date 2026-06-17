import Lenis from "lenis";
import { gsap, ScrollTrigger } from "./scrollTriggers";

let lenisInstance: Lenis | null = null;

export function getLenis(): Lenis | null {
  return lenisInstance;
}

export function scrollToId(id: string) {
  const target = document.getElementById(id);
  if (!target) return;
  if (lenisInstance) lenisInstance.scrollTo(target, { offset: -10, duration: 1.2 });
  else target.scrollIntoView({ behavior: "smooth" });
}

/** Initialise Lenis smooth scroll and wire it into GSAP's ticker + ScrollTrigger. */
export function initLenis(): () => void {
  const reduce =
    typeof window !== "undefined" &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reduce) return () => {};

  const lenis = new Lenis({ duration: 1.15, smoothWheel: true });
  lenisInstance = lenis;

  lenis.on("scroll", ScrollTrigger.update);
  const raf = (time: number) => lenis.raf(time * 1000);
  gsap.ticker.add(raf);
  gsap.ticker.lagSmoothing(0);

  return () => {
    gsap.ticker.remove(raf);
    lenis.destroy();
    lenisInstance = null;
  };
}
