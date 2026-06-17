"use client";

import dynamic from "next/dynamic";
import { useEffect, useState } from "react";

const Diorama = dynamic(() => import("@/components/diorama/diorama"), {
  ssr: false,
  loading: () => <Loader />,
});

function Loader() {
  return (
    <div className="grid h-[100svh] w-full place-items-center bg-bg">
      <div className="flex flex-col items-center gap-4">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-line border-t-gold" />
        <span className="font-mono text-[11px] uppercase tracking-[0.22em] text-muted">
          Atelier wird geladen
        </span>
      </div>
    </div>
  );
}

export default function AtelierPage() {
  // ensure client-only mount (WebGL)
  const [ready, setReady] = useState(false);
  useEffect(() => setReady(true), []);
  if (!ready) return <Loader />;
  return (
    <main className="h-[100svh] w-full overflow-hidden bg-bg">
      <Diorama />
    </main>
  );
}
