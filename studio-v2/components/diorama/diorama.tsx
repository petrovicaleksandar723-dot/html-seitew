"use client";

import { useState } from "react";
import { Canvas } from "@react-three/fiber";
import { EffectComposer, Bloom, Vignette } from "@react-three/postprocessing";
import * as THREE from "three";
import { AnimatePresence, motion } from "framer-motion";
import { Scene, type ZoneId } from "@/components/diorama/scene";

const INFO: Record<ZoneId, { title: string; tag: string; body: string }> = {
  produktion: {
    title: "Produktion",
    tag: "Dreh · Licht · Regie",
    body: "Wir drehen deinen Content vor Ort und im Studio — Kamera, Licht und Inszenierung, die deinen Betrieb premium aussehen lassen.",
  },
  schnitt: {
    title: "Schnitt & Post",
    tag: "Edit · Color · Sound",
    body: "Aus Rohmaterial wird ein Reel, das verkauft: schneller Schnitt, sauberes Color-Grading und Sounddesign, das hängen bleibt.",
  },
  pipeline: {
    title: "Content-System",
    tag: "Planung · Workflow",
    body: "Von der Idee bis zur Veröffentlichung läuft alles wie am Fließband — konstant, planbar und ohne Agentur-Chaos.",
  },
  marke: {
    title: "Markenwelt",
    tag: "Bildsprache · Vorlagen",
    body: "Eine konsistente visuelle Identität: Vorlagen, Farbwelt und ein Auftritt mit echtem Wiedererkennungswert.",
  },
};

export default function Diorama() {
  const [active, setActive] = useState<ZoneId | null>(null);

  return (
    <div className="relative h-[100svh] w-full">
      <Canvas
        dpr={[1, 1.5]}
        performance={{ min: 0.5 }}
        gl={{
          antialias: true,
          powerPreference: "high-performance",
          toneMapping: THREE.ACESFilmicToneMapping,
          toneMappingExposure: 1.05,
        }}
        onPointerMissed={() => setActive(null)}
      >
        <color attach="background" args={["#0b0a08"]} />
        <fog attach="fog" args={["#0b0a08", 28, 52]} />
        <Scene active={active} onSelect={setActive} />
        <EffectComposer multisampling={0}>
          <Bloom intensity={0.6} luminanceThreshold={0.7} luminanceSmoothing={0.25} mipmapBlur radius={0.6} />
          <Vignette eskil={false} offset={0.28} darkness={0.7} />
        </EffectComposer>
      </Canvas>

      {/* top-left brand */}
      <div className="pointer-events-none absolute left-0 top-0 p-6 sm:p-8">
        <div className="flex items-center gap-2.5">
          <span className="grid h-7 w-7 place-items-center rounded-[7px] bg-gradient-to-br from-gold-bright to-gold-deep text-[13px] font-extrabold text-[#1a1206]">
            C
          </span>
          <span className="font-display text-[15px] font-bold tracking-tight text-ink">
            Clean Lines <span className="text-muted">Studios</span>
          </span>
        </div>
      </div>

      {/* hint */}
      <div className="pointer-events-none absolute bottom-6 left-1/2 -translate-x-1/2 text-center">
        <p className="font-mono text-[11px] uppercase tracking-[0.22em] text-white/45">
          Tippe die Marker · zieh die Maus zum Drehen
        </p>
      </div>

      {/* info panel */}
      <AnimatePresence>
        {active && (
          <motion.aside
            key={active}
            initial={{ opacity: 0, x: 40 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 40 }}
            transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
            className="absolute right-5 top-1/2 w-[min(360px,86vw)] -translate-y-1/2 rounded-2xl border border-line bg-bg/80 p-7 backdrop-blur-xl"
          >
            <div className="font-mono text-[10px] uppercase tracking-[0.2em] text-gold">
              {INFO[active].tag}
            </div>
            <h2 className="mt-3 font-display text-[30px] font-extrabold tracking-tight text-ink">
              {INFO[active].title}
            </h2>
            <p className="mt-3 font-body text-[14.5px] leading-relaxed text-dim">
              {INFO[active].body}
            </p>
            <div className="mt-6 flex gap-3">
              <a
                href="#"
                className="rounded-full bg-gradient-to-br from-gold-bright to-gold-deep px-5 py-2.5 font-display text-[13px] font-bold text-[#1a1206]"
              >
                Anfragen
              </a>
              <button
                onClick={() => setActive(null)}
                className="rounded-full border border-white/20 px-5 py-2.5 font-display text-[13px] font-bold text-ink transition-colors hover:border-white/40"
              >
                Schließen
              </button>
            </div>
          </motion.aside>
        )}
      </AnimatePresence>
    </div>
  );
}
