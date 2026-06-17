"use client";

import { useEffect, useRef, useState, type ReactNode } from "react";

/**
 * Mounts children only while near the viewport and unmounts when far away.
 * Used to release WebGL/video decoders for heavy canvases that are off-screen.
 */
export function InView({
  children,
  fallback = null,
  rootMargin = "400px",
}: {
  children: ReactNode;
  fallback?: ReactNode;
  rootMargin?: string;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const [active, setActive] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const io = new IntersectionObserver(
      ([entry]) => setActive(entry.isIntersecting),
      { rootMargin }
    );
    io.observe(el);
    return () => io.disconnect();
  }, [rootMargin]);

  return (
    <div ref={ref} className="absolute inset-0">
      {active ? children : fallback}
    </div>
  );
}
