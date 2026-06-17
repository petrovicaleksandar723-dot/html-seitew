import { useEffect, useRef } from "react";
import { Check } from "lucide-react";
import { packages, mailto } from "../../content/siteContent";
import SectionNumber from "../ui/SectionNumber";
import SplitHeadline from "../ui/SplitHeadline";
import MagneticButton from "../ui/MagneticButton";
import { gsap } from "../../motion/scrollTriggers";

/** Scene 9 — Packages / Premium System Tiers. 3D glass tiers. */
export default function PackagesSection() {
  const root = useRef<HTMLElement>(null);

  useEffect(() => {
    const el = root.current;
    if (!el) return;
    const ctx = gsap.context(() => {
      gsap.from(el.querySelectorAll(".pkg"), {
        y: 90,
        opacity: 0,
        rotateX: 12,
        duration: 1.1,
        ease: "expo.out",
        stagger: 0.12,
        scrollTrigger: { trigger: el, start: "top 70%" },
      });
    }, el);
    return () => ctx.revert();
  }, []);

  return (
    <section className="packages section scene-pad" id="packages" ref={root}>
      <div className="shell">
        <div className="scene-head">
          <SectionNumber num="06" label="Pakete" />
          <div className="eyebrow">{packages.eyebrow}</div>
          <SplitHeadline text={packages.headline} />
        </div>

        <div className="pkg-deck">
          {packages.items.map((pkg) => (
            <article key={pkg.name} className={`pkg ${pkg.featured ? "is-featured" : ""}`}>
              {pkg.featured && <span className="pkg__badge">Beliebt</span>}
              <div className="pkg__name">{pkg.name}</div>
              <div className="pkg__price">
                <b>{pkg.price}</b>
                <span>{pkg.per}</span>
              </div>
              <p className="pkg__desc">{pkg.desc}</p>
              <ul className="pkg__feat">
                {pkg.features.map((f) => (
                  <li key={f}>
                    <Check size={17} />
                    {f}
                  </li>
                ))}
              </ul>
              <MagneticButton
                variant={pkg.featured ? "primary" : "ghost"}
                href={mailto(`Anfrage Paket: ${pkg.name} (${pkg.price}${pkg.per})`)}
              >
                {pkg.name} anfragen
              </MagneticButton>
            </article>
          ))}
        </div>

        <div className="pkg__notes">
          {packages.notes.map((n) => (
            <p key={n}>{n}</p>
          ))}
        </div>
      </div>
    </section>
  );
}
