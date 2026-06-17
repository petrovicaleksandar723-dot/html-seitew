"use client";

import { usePathname } from "next/navigation";

export function Grain() {
  const pathname = usePathname();
  if (pathname?.startsWith("/atelier")) return null;
  return <div className="grain" aria-hidden />;
}
