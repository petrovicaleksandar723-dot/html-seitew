"use client";

import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import { Overlay } from "@/components/cosmos/overlay";
import { Cursor } from "@/components/cosmos/cursor";
import { Preloader } from "@/components/cosmos/preloader";

const CosmosScene = dynamic(
  () => import("@/components/cosmos/scene").then((m) => m.CosmosScene),
  { ssr: false }
);

function useWebGLCapable() {
  const [ok, setOk] = useState<boolean | null>(null);
  useEffect(() => {
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const coarse = window.matchMedia("(pointer: coarse)").matches;
    let gl = false;
    try {
      gl = !!document.createElement("canvas").getContext("webgl2");
    } catch {
      gl = false;
    }
    // full WebGL flight on capable desktops; lighter experience elsewhere
    setOk(gl && !reduce && !coarse);
  }, []);
  return ok;
}

export default function ExperiencePage() {
  const capable = useWebGLCapable();
  const [entered, setEntered] = useState(false);

  // lock scroll until the user enters the experience
  useEffect(() => {
    if (capable && !entered) {
      document.documentElement.style.overflow = "hidden";
    } else {
      document.documentElement.style.overflow = "";
    }
    return () => {
      document.documentElement.style.overflow = "";
    };
  }, [capable, entered]);

  if (capable === null) {
    return <div className="min-h-screen bg-bg" />;
  }

  return (
    <main className="relative bg-bg">
      {capable ? (
        <>
          <CosmosScene />
          <Preloader onEnter={() => setEntered(true)} />
        </>
      ) : (
        // mobile / reduced-motion fallback: static premium backdrop, full content
        <div
          aria-hidden
          className="pointer-events-none fixed inset-0 -z-10"
          style={{
            background:
              "radial-gradient(70% 50% at 50% 0%, rgba(216,178,116,0.16), transparent 70%), radial-gradient(50% 40% at 100% 100%, rgba(216,178,116,0.08), transparent 70%), #060504",
          }}
        />
      )}
      <Cursor />
      <Overlay />
    </main>
  );
}
