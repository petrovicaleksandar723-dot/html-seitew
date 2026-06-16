import { gsap } from "./scrollTriggers";

type Args = {
  section: HTMLElement;
  after: HTMLElement;
  divider: HTMLElement;
};

/** Pinned scroll-driven clip-path wipe from the "before" to the "after" state. */
export function buildTransformation({ section, after, divider }: Args) {
  const tl = gsap.timeline({
    scrollTrigger: {
      trigger: section,
      start: "top top",
      end: "+=130%",
      pin: true,
      scrub: 0.6,
      invalidateOnRefresh: true,
    },
  });

  tl.fromTo(after, { clipPath: "inset(0 0 0 100%)" }, { clipPath: "inset(0 0 0 0%)", ease: "none" }, 0).fromTo(
    divider,
    { left: "100%" },
    { left: "0%", ease: "none" },
    0
  );

  return tl;
}
