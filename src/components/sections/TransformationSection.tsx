import { useEffect, useRef } from "react";
import { transformation, mailto } from "../../content/siteContent";
import MagneticButton from "../ui/MagneticButton";
import { buildTransformation } from "../../motion/transformationTimeline";
import { gsap } from "../../motion/scrollTriggers";

/** Scene 7 — Before/After Transformation. Pinned gold wipe with final.mp4 reveal. */
export default function TransformationSection() {
  const section = useRef<HTMLElement>(null);
  const after = useRef<HTMLDivElement>(null);
  const line = useRef<HTMLDivElement>(null);
  const video = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    const sec = section.current;
    const a = after.current;
    const l = line.current;
    if (!sec || !a || !l) return;
    if (window.matchMedia("(pointer: coarse)").matches) return;
    const ctx = gsap.context(() => {
      buildTransformation(sec, a, l);
    }, sec);
    return () => ctx.revert();
  }, []);

  useEffect(() => {
    const v = video.current;
    if (!v) return;
    const io = new IntersectionObserver((entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) {
          if (!v.src) v.src = transformation.video;
          v.play().catch(() => {});
        } else v.pause();
      });
    });
    io.observe(v);
    return () => io.disconnect();
  }, []);

  return (
    <section className="transform section" id="transformation" ref={section}>
      <div className="transform__pin">
        <div className="tf-eyebrow">
          <span className="eyebrow">{transformation.eyebrow}</span>
          <h2 className="tf-title">{transformation.headline}</h2>
        </div>

        {/* BEFORE */}
        <div className="tf-layer tf-before">
          <div className="tf-col">
            <div className="tf-tag">{transformation.before.label}</div>
            <ul className="tf-list">
              {transformation.before.items.map((it) => (
                <li key={it}>{it}</li>
              ))}
            </ul>
          </div>
        </div>

        {/* AFTER (revealed by wipe) */}
        <div className="tf-layer tf-after" ref={after}>
          <div className="tf-video">
            <video ref={video} muted loop playsInline preload="none" />
          </div>
          <div className="tf-col">
            <div className="tf-tag">{transformation.after.label}</div>
            <ul className="tf-list">
              {transformation.after.items.map((it) => (
                <li key={it}>{it}</li>
              ))}
            </ul>
            <div className="tf-cta">
              <MagneticButton href={mailto("Content-Preview für meinen Betrieb")}>
                {transformation.cta}
              </MagneticButton>
            </div>
          </div>
        </div>

        <div className="tf-line" ref={line} />
      </div>
    </section>
  );
}
