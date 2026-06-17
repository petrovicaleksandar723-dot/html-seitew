import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

export { gsap, ScrollTrigger };

/**
 * Run a setup function inside a GSAP context scoped to `scope`, returning a
 * cleanup callback. Use inside useEffect/useLayoutEffect so every ScrollTrigger
 * and tween created in `fn` is reverted automatically on unmount.
 */
export function withCtx(
  scope: Element | null,
  fn: (self: gsap.Context) => void
): () => void {
  const ctx = gsap.context(fn, scope ?? undefined);
  return () => ctx.revert();
}

/** Fade + rise reveal for a set of elements as they enter the viewport. */
export function revealUp(
  targets: gsap.TweenTarget,
  trigger: Element,
  opts: { stagger?: number; y?: number; start?: string } = {}
): void {
  const { stagger = 0.12, y = 60, start = "top 80%" } = opts;
  gsap.from(targets, {
    y,
    opacity: 0,
    duration: 1.1,
    ease: "power3.out",
    stagger,
    scrollTrigger: { trigger, start },
  });
}

export function refreshScrollTriggers(): void {
  ScrollTrigger.refresh();
}
