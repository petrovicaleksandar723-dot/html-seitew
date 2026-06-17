import { useEffect, useRef } from "react";

/** Lazily autoplays a muted, looping atmosphere video once it scrolls into view.
 *  Always sits under a dark veil so overlaid text stays readable. */
export function VideoPanel({
  src,
  className = "",
  veil = true,
  fit = "cover",
}: {
  src: string;
  className?: string;
  veil?: boolean;
  fit?: "cover" | "contain";
}) {
  const ref = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    const v = ref.current;
    if (!v) return;
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((x) => {
          if (x.isIntersecting) {
            if (!v.src) v.src = src;
            v.play().catch(() => {});
          } else {
            v.pause();
          }
        });
      },
      { threshold: 0.05 }
    );
    io.observe(v);
    return () => io.disconnect();
  }, [src]);

  return (
    <div className={`vpanel ${className}`}>
      <video ref={ref} muted loop playsInline preload="metadata" style={{ objectFit: fit }} />
      {veil && <div className="vpanel-veil" />}
    </div>
  );
}
