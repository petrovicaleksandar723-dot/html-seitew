import { gsap, ScrollTrigger } from "./scrollTriggers";

type Args = {
  section: HTMLElement;
  track: HTMLElement;
  cards: HTMLElement[];
  onProgress: (index: number, progress: number) => void;
};

/** Pinned horizontal "Reel Cinema" scroll. Returns the created ScrollTrigger. */
export function buildReelCinema({ section, track, cards, onProgress }: Args) {
  const dist = () => Math.max(0, track.scrollWidth - window.innerWidth);

  const tween = gsap.to(track, {
    x: () => -dist(),
    ease: "none",
    scrollTrigger: {
      trigger: section,
      start: "top top",
      end: () => "+=" + dist(),
      pin: true,
      scrub: 1,
      invalidateOnRefresh: true,
      onUpdate: (self) => {
        const idx = Math.min(cards.length - 1, Math.round(self.progress * (cards.length - 1)));
        onProgress(idx, self.progress);
      },
    },
  });

  return tween.scrollTrigger as ScrollTrigger;
}
