import { VideoPanel } from "./VideoPanel";

/** A very dark, low-opacity cinematic video behind a section for atmosphere.
 *  Sits at z-0; section content (.wrap) renders above it. */
export function SectionVideoBg({ src, opacity = 0.12 }: { src: string; opacity?: number }) {
  return (
    <div className="section-vbg" aria-hidden style={{ opacity }}>
      <VideoPanel src={src} veil={false} />
    </div>
  );
}
