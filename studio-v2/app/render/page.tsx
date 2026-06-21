"use client";

import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import { Overlay } from "@/components/render/overlay";
import { Cursor } from "@/components/cosmos/cursor";
import { Preloader } from "@/components/cosmos/preloader";

const RenderScene = dynamic(
  () => import("@/components/render/scene").then((m) => m.RenderScene),
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
    setOk(gl && !reduce && !coarse);
  }, []);
  return ok;
}

export default function RenderPage() {
  const capable = useWebGLCapable();
  const [entered, setEntered] = useState(false);

  useEffect(() => {
    document.documentElement.style.overflow = capable && !entered ? "hidden" : "";
    return () => {
      document.documentElement.style.overflow = "";
    };
  }, [capable, entered]);

  if (capable === null) return <div className="min-h-screen bg-bg" />;

  return (
    <main className="relative">
      {capable ? (
        <>
          <RenderScene />
          <Preloader onEnter={() => setEntered(true)} />
        </>
      ) : (
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
