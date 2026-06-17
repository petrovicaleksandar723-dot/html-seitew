import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

/**
 * Pinned before/after wipe. As the user scrolls, a gold vertical line sweeps
 * across the screen and the cinematic "after" layer is revealed via clip-path.
 */
export function buildTransformation(
  section: HTMLElement,
  afterLayer: HTMLElement,
  line: HTMLElement
): ScrollTrigger {
  const tl = gsap.timeline({
    scrollTrigger: {
      trigger: section,
      start: "top top",
      end: "+=140%",
      pin: true,
      scrub: 0.8,
      invalidateOnRefresh: true,
    },
  });

  tl.fromTo(
    afterLayer,
    { clipPath: "inset(0 0 0 100%)" },
    { clipPath: "inset(0 0 0 0%)", ease: "none" },
    0
  ).fromTo(
    line,
    { left: "100%" },
    { left: "0%", ease: "none" },
    0
  );

  return tl.scrollTrigger as ScrollTrigger;
}
