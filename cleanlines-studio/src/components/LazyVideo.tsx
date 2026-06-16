import { useEffect, useRef } from "react";

/** Loads + plays only while on screen; pauses off screen (keeps mobile light). */
export function LazyVideo({ src, poster }: { src: string; poster?: string }) {
  const ref = useRef<HTMLVideoElement>(null);
  useEffect(() => {
    const v = ref.current;
    if (!v) return;
    const io = new IntersectionObserver(
      (es) => {
        es.forEach((en) => {
          if (en.isIntersecting) {
            if (!v.src) v.src = src;
            const p = v.play();
            if (p && p.catch) p.catch(() => {});
          } else {
            try {
              v.pause();
            } catch {
              /* ignore */
            }
          }
        });
      },
      { threshold: 0.5 }
    );
    io.observe(v);
    return () => io.disconnect();
  }, [src]);
  return <video ref={ref} poster={poster} muted loop playsInline preload="none" />;
}
