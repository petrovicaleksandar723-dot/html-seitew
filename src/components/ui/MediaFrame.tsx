import { useEffect, useRef } from "react";

/** A gold-framed, lazily played video surface. */
export function MediaFrame({
  src,
  className = "",
  active = true,
}: {
  src: string;
  className?: string;
  active?: boolean;
}) {
  const ref = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    const v = ref.current;
    if (!v) return;
    if (active) {
      if (!v.src) v.src = src;
      v.play().catch(() => {});
    } else {
      v.pause();
    }
  }, [active, src]);

  return (
    <div className={`media-frame ${className}`}>
      <video ref={ref} muted loop playsInline preload="none" />
    </div>
  );
}
