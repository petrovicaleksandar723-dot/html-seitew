import { VideoPanel } from "./VideoPanel";

const PANELS = [
  { src: "/assets/videos/reel-1.mp4", cls: "a" },
  { src: "/assets/videos/show-1.mp4", cls: "b" },
  { src: "/assets/videos/reel-3.mp4", cls: "c" },
  { src: "/assets/videos/show-4.mp4", cls: "d" },
  { src: "/assets/videos/reel-4.mp4", cls: "e" },
];

/** A field of slowly drifting cinematic video panels behind the hero — the
 *  "weltraum mit videos". Desktop-only (hidden on small screens for perf). */
export function HeroMedia() {
  return (
    <div className="hero-media" aria-hidden>
      {PANELS.map((p) => (
        <VideoPanel key={p.cls} src={p.src} className={`hm ${p.cls}`} />
      ))}
    </div>
  );
}
