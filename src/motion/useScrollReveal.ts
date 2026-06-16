import { useEffect, RefObject } from "react";
import { gsap } from "./scrollTriggers";
import { splitWords } from "./splitText";

/** Animates masked headlines ([data-split]), fade items ([data-fade]) and
 *  .reveal blocks within a section as it enters the viewport. */
export function useScrollReveal(ref: RefObject<HTMLElement>) {
  useEffect(() => {
    const scope = ref.current;
    if (!scope) return;
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduce) {
      scope.querySelectorAll<HTMLElement>(".reveal").forEach((e) => (e.style.opacity = "1"));
      return;
    }

    const ctx = gsap.context(() => {
      gsap.utils.toArray<HTMLElement>("[data-split]").forEach((h) => {
        const words = splitWords(h);
        gsap.set(words, { yPercent: 118 });
        gsap.to(words, {
          yPercent: 0,
          duration: 1,
          stagger: 0.04,
          ease: "expo.out",
          scrollTrigger: { trigger: h, start: "top 86%" },
        });
      });

      gsap.utils.toArray<HTMLElement>("[data-fade]").forEach((el) => {
        gsap.fromTo(
          el,
          { y: 24, opacity: 0 },
          { y: 0, opacity: 1, duration: 0.9, ease: "power3.out", scrollTrigger: { trigger: el, start: "top 90%" } }
        );
      });

      gsap.utils.toArray<HTMLElement>(".reveal").forEach((el) => {
        gsap.fromTo(
          el,
          { y: 34, opacity: 0 },
          { y: 0, opacity: 1, duration: 1, ease: "power3.out", scrollTrigger: { trigger: el, start: "top 90%" } }
        );
      });
    }, scope);

    return () => ctx.revert();
  }, [ref]);
}
