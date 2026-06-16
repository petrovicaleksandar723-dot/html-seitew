import { gsap } from "./scrollTriggers";

/** Intro reveal for the hero: masked headline lines rise in, then UI fades up. */
export function buildHeroIntro(scope: HTMLElement, delay = 0.2) {
  const tl = gsap.timeline({ delay });

  const lines = scope.querySelectorAll<HTMLElement>(".hero-line");
  gsap.set(lines, { yPercent: 118 });
  tl.to(lines, { yPercent: 0, duration: 1.1, stagger: 0.09, ease: "expo.out" }, 0);

  const fades = scope.querySelectorAll<HTMLElement>("[data-fade]");
  tl.fromTo(
    fades,
    { y: 24, opacity: 0 },
    { y: 0, opacity: 1, duration: 0.9, stagger: 0.08, ease: "power3.out" },
    "-=0.6"
  );

  return tl;
}
