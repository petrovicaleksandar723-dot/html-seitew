import { useEffect, useRef } from "react";
import { finalCTA, mailto, whatsapp, waMessage } from "../../content/siteContent";
import MagneticButton from "../ui/MagneticButton";
import SplitHeadline from "../ui/SplitHeadline";
import { gsap } from "../../motion/scrollTriggers";

/** Scene 12 — Final Cinematic CTA. final.mp4 as a light wall behind the call. */
export default function FinalCTASection() {
  const root = useRef<HTMLElement>(null);
  const video = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    const el = root.current;
    const v = video.current;
    if (!el) return;
    const ctx = gsap.context(() => {
      gsap.from(el.querySelectorAll(".final__cta, .final__trust, .eyebrow"), {
        y: 40,
        opacity: 0,
        duration: 1,
        stagger: 0.12,
        ease: "expo.out",
        scrollTrigger: { trigger: el, start: "top 65%" },
      });
    }, el);

    // lazy-start the background video — prefer the cinematic Higgsfield film,
    // fall back to the bundled clip if the remote can't load.
    if (v) {
      v.onerror = () => {
        if (v.src.indexOf(finalCTA.video) === -1) v.src = finalCTA.video;
      };
      const io = new IntersectionObserver((entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            if (!v.src) v.src = finalCTA.videoRemote || finalCTA.video;
            v.play().catch(() => {});
          } else v.pause();
        });
      });
      io.observe(v);
      return () => {
        io.disconnect();
        ctx.revert();
      };
    }
    return () => ctx.revert();
  }, []);

  return (
    <section className="final section" id="final-cta" ref={root}>
      <div className="final__video" data-parallax="-10">
        <video ref={video} muted loop playsInline preload="none" />
      </div>

      <div className="final__inner shell">
        <div className="eyebrow">{finalCTA.eyebrow}</div>
        <SplitHeadline text={finalCTA.headline} as="h2" className="headline-section final__headline" />
        <p className="hero__subline" style={{ maxWidth: "52ch" }}>
          {finalCTA.subline}
        </p>
        <div className="final__cta">
          <MagneticButton href={mailto("Kostenlose Content-Preview")}>
            {finalCTA.ctaPrimary}
          </MagneticButton>
          <MagneticButton variant="ghost" href={whatsapp(waMessage)} external>
            {finalCTA.ctaSecondary}
          </MagneticButton>
        </div>
        <div className="final__trust">
          {finalCTA.trust.map((t) => (
            <span key={t}>{t}</span>
          ))}
        </div>
      </div>
    </section>
  );
}
