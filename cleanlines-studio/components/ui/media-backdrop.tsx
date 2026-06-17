"use client";

import { useEffect, useRef } from "react";

/**
 * Cinematic media backdrop — a dimmed grid of looping clips behind a section,
 * framed by radial + top/bottom gradients so content stays readable.
 * Plays only while the section is in view (IntersectionObserver) to stay light.
 */
export function MediaBackdrop({
  videos,
  opacity = 0.14,
}: {
  videos: string[];
  opacity?: number;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const vids = useRef<HTMLVideoElement[]>([]);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const io = new IntersectionObserver(
      ([entry]) => {
        vids.current.forEach((v) => {
          if (!v) return;
          if (entry.isIntersecting) v.play().catch(() => {});
          else v.pause();
        });
      },
      { threshold: 0.04 }
    );
    io.observe(el);
    return () => io.disconnect();
  }, []);

  const cols =
    videos.length >= 4
      ? "md:grid-cols-4"
      : videos.length === 3
        ? "md:grid-cols-3"
        : "md:grid-cols-2";

  return (
    <div ref={ref} className="absolute inset-0 z-0">
      <div className={`grid h-full grid-cols-2 ${cols}`}>
        {videos.map((src, i) => (
          <video
            key={i}
            ref={(el) => {
              if (el) vids.current[i] = el;
            }}
            className="h-full w-full scale-105 object-cover"
            style={{ opacity }}
            src={src}
            muted
            loop
            playsInline
            preload="none"
          />
        ))}
      </div>
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(120%_120%_at_50%_40%,rgba(5,5,5,0.5)_28%,rgba(5,5,5,0.94)_100%)]" />
      <div className="pointer-events-none absolute inset-x-0 top-0 h-40 bg-gradient-to-b from-bg to-transparent" />
      <div className="pointer-events-none absolute inset-x-0 bottom-0 h-40 bg-gradient-to-t from-bg to-transparent" />
    </div>
  );
}
