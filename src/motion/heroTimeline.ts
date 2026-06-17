import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { splitWords } from "./splitText";

gsap.registerPlugin(ScrollTrigger);

/** Intro reveal for the hero — runs once after the preloader exits. */
export function playHeroIntro(root: HTMLElement): gsap.core.Timeline {
  const tl = gsap.timeline({ defaults: { ease: "expo.out" } });

  const eyebrow = root.querySelector(".hero__eyebrow");
  const headline = root.querySelector<HTMLElement>(".hero__headline");
  const subline = root.querySelector(".hero__subline");
  const cta = root.querySelector(".hero__cta");
  const hud = root.querySelectorAll(".hero__hud .hud-row");
  const trust = root.querySelector(".hero__trust");
  const scroll = root.querySelector(".hero__scroll");

  if (eyebrow) tl.from(eyebrow, { y: 30, opacity: 0, duration: 1 }, 0);

  if (headline) {
    const words = splitWords(headline);
    gsap.set(words, { yPercent: 110 });
    tl.to(words, { yPercent: 0, duration: 1.3, stagger: 0.09 }, 0.1);
  }
  if (subline) tl.from(subline, { y: 40, opacity: 0, duration: 1.1 }, 0.5);
  if (cta) tl.from(cta, { y: 30, opacity: 0, duration: 1 }, 0.65);
  if (hud.length) tl.from(hud, { x: 30, opacity: 0, duration: 0.9, stagger: 0.1 }, 0.5);
  if (trust) tl.from(trust, { opacity: 0, duration: 1 }, 0.8);
  if (scroll) tl.from(scroll, { opacity: 0, duration: 1 }, 1);

  return tl;
}

/**
 * Scroll-linked hero parallax: the foreground copy drifts up and fades while the
 * section pins briefly, letting the WebGL engine carry the transition.
 */
export function buildHeroScroll(root: HTMLElement): void {
  const inner = root.querySelector(".hero__inner");
  if (inner) {
    gsap.to(inner, {
      yPercent: -18,
      opacity: 0,
      ease: "none",
      scrollTrigger: {
        trigger: root,
        start: "top top",
        end: "bottom top",
        scrub: true,
      },
    });
  }
}
