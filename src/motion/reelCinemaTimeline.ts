import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

export interface ReelCinemaControls {
  /** Called with the index of the card currently centred in the viewport. */
  onActive: (index: number) => void;
}

/**
 * Pinned horizontal scroll for the Reel Cinema. The vertical scroll distance is
 * translated into horizontal movement of the track, and the centred card index
 * is reported back so the component can drive the active state + video playback.
 */
export function buildReelCinema(
  section: HTMLElement,
  track: HTMLElement,
  count: number,
  controls: ReelCinemaControls
): ScrollTrigger {
  const getDistance = () => track.scrollWidth - window.innerWidth;

  const tween = gsap.to(track, {
    x: () => -getDistance(),
    ease: "none",
    scrollTrigger: {
      trigger: section,
      start: "top top",
      end: () => `+=${getDistance() + window.innerHeight}`,
      pin: true,
      scrub: 1,
      invalidateOnRefresh: true,
      anticipatePin: 1,
      onUpdate: (self) => {
        const idx = Math.round(self.progress * (count - 1));
        controls.onActive(idx);
      },
    },
  });

  return tween.scrollTrigger as ScrollTrigger;
}
