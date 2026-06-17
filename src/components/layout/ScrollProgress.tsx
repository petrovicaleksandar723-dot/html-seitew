import { useEffect, useRef } from "react";
import { gsap, ScrollTrigger } from "../../motion/scrollTriggers";

/** Thin gold progress bar tracking total page scroll. */
export default function ScrollProgress() {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const st = ScrollTrigger.create({
      start: 0,
      end: "max",
      onUpdate: (self) => {
        gsap.set(el, { scaleX: self.progress });
      },
    });
    return () => st.kill();
  }, []);

  return <div ref={ref} className="scroll-progress" aria-hidden />;
}
