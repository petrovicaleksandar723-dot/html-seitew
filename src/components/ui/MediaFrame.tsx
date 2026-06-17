import { useEffect, useRef } from "react";

interface Props {
  src: string;
  className?: string;
  /** Lazy-load: only start playing once the frame is near the viewport. */
  lazy?: boolean;
  poster?: string;
}

/**
 * A bordered media frame wrapping a muted, looping, autoplaying video.
 * Honours reduced-motion and only loads heavy video when near the viewport.
 */
export default function MediaFrame({ src, className = "", lazy = true, poster }: Props) {
  const ref = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    const video = ref.current;
    if (!video) return;
    if (!lazy) {
      video.src = src;
      return;
    }
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            if (!video.src) video.src = src;
            video.play().catch(() => {});
          } else {
            video.pause();
          }
        });
      },
      { rootMargin: "200px" }
    );
    io.observe(video);
    return () => io.disconnect();
  }, [src, lazy]);

  return (
    <div className={`media-frame ${className}`}>
      <video
        ref={ref}
        muted
        loop
        playsInline
        preload="metadata"
        poster={poster}
        {...(!lazy ? { src } : {})}
      />
    </div>
  );
}
