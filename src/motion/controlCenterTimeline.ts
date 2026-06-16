import { gsap } from "./scrollTriggers";

type Args = {
  section: HTMLElement;
  ipad: HTMLElement;
  apps: HTMLElement[];
};

/** Cinematic reveal: the tablet rotates from an angled cinematic pose into a
 *  front-facing "product demo" pose as the section scrolls into view, while the
 *  app modules stagger in. Returns a cleanup function. */
export function buildControlCenter({ section, ipad, apps }: Args) {
  const tl = gsap.timeline({
    scrollTrigger: {
      trigger: section,
      start: "top 78%",
      end: "top 22%",
      scrub: 0.7,
    },
  });
  tl.fromTo(
    ipad,
    { rotateY: -22, rotateX: 9, y: 60, scale: 0.94 },
    { rotateY: 0, rotateX: 0, y: 0, scale: 1, ease: "none" },
    0
  );

  const appsTl = gsap.from(apps, {
    opacity: 0,
    y: 18,
    scale: 0.9,
    stagger: 0.045,
    duration: 0.55,
    ease: "power3.out",
    scrollTrigger: { trigger: section, start: "top 60%" },
  });

  return () => {
    tl.scrollTrigger?.kill();
    tl.kill();
    appsTl.scrollTrigger?.kill();
    appsTl.kill();
  };
}
