import { useRef, useLayoutEffect, type ReactNode } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

type Props = {
  children: ReactNode;
  className?: string;
  y?: number;
  delay?: number;
  stagger?: boolean;
};

/** Cinematic scroll reveal. Animates the element (or its children when stagger). */
export function Reveal({ children, className = "", y = 44, delay = 0, stagger = false }: Props) {
  const ref = useRef<HTMLDivElement>(null);

  useLayoutEffect(() => {
    const el = ref.current;
    if (!el) return;
    if (window.matchMedia("(prefers-reduced-motion:reduce)").matches) {
      el.classList.add("ready");
      return;
    }
    const ctx = gsap.context(() => {
      el.classList.add("ready");
      const targets: gsap.TweenTarget = stagger ? Array.from(el.children) : el;
      gsap.from(targets, {
        opacity: 0,
        y,
        duration: 0.9,
        ease: "power3.out",
        delay,
        stagger: stagger ? 0.09 : 0,
        scrollTrigger: { trigger: el, start: "top 86%", once: true },
      });
    }, el);
    return () => ctx.revert();
  }, [y, delay, stagger]);

  return (
    <div ref={ref} className={"reveal " + className}>
      {children}
    </div>
  );
}
