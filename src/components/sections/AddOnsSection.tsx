import { useEffect, useRef } from "react";
import { addOns, mailto } from "../../content/siteContent";
import SectionNumber from "../ui/SectionNumber";
import SplitHeadline from "../ui/SplitHeadline";
import MagneticButton from "../ui/MagneticButton";
import { gsap } from "../../motion/scrollTriggers";

/** Scene 10 — Add-ons / Einzelaufträge. Premium horizontal product rows. */
export default function AddOnsSection() {
  const root = useRef<HTMLElement>(null);

  useEffect(() => {
    const el = root.current;
    if (!el) return;
    const ctx = gsap.context(() => {
      gsap.from(el.querySelectorAll(".addon-row"), {
        y: 50,
        opacity: 0,
        duration: 0.9,
        ease: "power3.out",
        stagger: 0.1,
        scrollTrigger: { trigger: el, start: "top 72%" },
      });
    }, el);
    return () => ctx.revert();
  }, []);

  return (
    <section className="addons section scene-pad" id="addons" ref={root}>
      <div className="shell">
        <div className="scene-head">
          <SectionNumber num="07" label="Einzelaufträge" />
          <div className="eyebrow">{addOns.eyebrow}</div>
          <SplitHeadline text={addOns.headline} />
          <p className="text-soft">{addOns.subline}</p>
        </div>

        <div className="addon-deck">
          {addOns.items.map((item) => (
            <div className="addon-row" key={item.name} data-cursor="hover">
              <div className="addon-name">{item.name}</div>
              <div className="addon-body">{item.body}</div>
              <div className="addon-price">{item.price}</div>
            </div>
          ))}
        </div>

        <div className="addon-cta">
          <MagneticButton href={mailto("Einzelauftrag Anfrage")}>{addOns.cta}</MagneticButton>
        </div>
      </div>
    </section>
  );
}
