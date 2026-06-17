import Lenis from "lenis";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

let lenis: Lenis | null = null;

/** Initialise Lenis smooth scroll wired into the GSAP ticker + ScrollTrigger. */
export function initLenis(): Lenis {
  if (lenis) return lenis;

  gsap.registerPlugin(ScrollTrigger);

  lenis = new Lenis({
    duration: 1.15,
    easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
    smoothWheel: true,
    wheelMultiplier: 1,
    touchMultiplier: 1.6,
  });

  lenis.on("scroll", ScrollTrigger.update);

  gsap.ticker.add((time) => {
    lenis?.raf(time * 1000);
  });
  gsap.ticker.lagSmoothing(0);

  return lenis;
}

export function getLenis(): Lenis | null {
  return lenis;
}

export function scrollToTarget(target: string | HTMLElement, offset = 0): void {
  lenis?.scrollTo(target, { offset, duration: 1.4 });
}

export function stopLenis(): void {
  lenis?.stop();
}

export function startLenis(): void {
  lenis?.start();
}

export function destroyLenis(): void {
  lenis?.destroy();
  lenis = null;
}
