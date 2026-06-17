import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

/**
 * Scroll-scrubbed production pipeline: a gold signal travels along the rail,
 * progressively filling the line and lighting up each step as it passes.
 */
export function buildPipeline(
  section: HTMLElement,
  rail: HTMLElement,
  signal: HTMLElement,
  steps: HTMLElement[]
): ScrollTrigger {
  const tl = gsap.timeline({
    scrollTrigger: {
      trigger: section,
      start: "top 70%",
      end: "bottom 75%",
      scrub: 0.8,
    },
  });

  tl.to(rail, { scaleX: 1, ease: "none" }, 0).to(
    signal,
    { left: "100%", ease: "none" },
    0
  );

  steps.forEach((step, i) => {
    const at = (i / Math.max(1, steps.length - 1)) * 0.85;
    tl.add(() => step.classList.add("is-on"), at);
    // also reveal content
    tl.from(
      step.querySelectorAll(".pipe-num, .pipe-title, .pipe-body"),
      { y: 24, opacity: 0, duration: 0.4, stagger: 0.05, ease: "power3.out" },
      at
    );
  });

  return tl.scrollTrigger as ScrollTrigger;
}
