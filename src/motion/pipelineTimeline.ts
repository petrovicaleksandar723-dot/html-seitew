import { gsap } from "./scrollTriggers";

type Args = {
  trigger: HTMLElement;
  fill: HTMLElement;
  steps: HTMLElement[];
};

/** Scroll-scrubbed gold signal line that activates each pipeline node in turn. */
export function buildPipeline({ trigger, fill, steps }: Args) {
  return gsap.to(fill, {
    width: "100%",
    ease: "none",
    scrollTrigger: {
      trigger,
      start: "top 70%",
      end: "bottom 75%",
      scrub: 0.8,
      onUpdate: (self) => {
        steps.forEach((s, i) => {
          s.classList.toggle("on", self.progress >= i / steps.length);
        });
      },
    },
  });
}
