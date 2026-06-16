import { useRef } from "react";
import { Check } from "lucide-react";
import { PACKAGES, mailtoHref } from "../../content/siteContent";
import { KineticLabel } from "../ui/KineticLabel";
import { SplitHeadline } from "../ui/SplitHeadline";
import { SectionNumber } from "../ui/SectionNumber";
import { MagneticButton } from "../ui/MagneticButton";
import { useScrollReveal } from "../../motion/useScrollReveal";

export function PackagesSection() {
  const ref = useRef<HTMLElement>(null);
  useScrollReveal(ref);

  return (
    <section id="packages" className="scene" ref={ref}>
      <div className="wrap">
        <div className="sol-head">
          <SectionNumber n="07" />
          <div>
            <KineticLabel>Pakete</KineticLabel>
            <SplitHeadline text="Wähl dein Content-System." gold="Content-System." />
          </div>
        </div>
        <p className="lede" data-fade style={{ margin: "-30px 0 10px" }}>
          Planbar. Fair. Monatlich kündbar. Keine Einrichtungsgebühr, keine versteckten Kosten.
        </p>

        <div className="tiers">
          {PACKAGES.map((p) => (
            <div className={`tier reveal ${p.featured ? "feat" : ""}`} key={p.id}>
              {p.featured && <span className="badge">Beliebt</span>}
              <h3>{p.name}</h3>
              <p className="desc">{p.desc}</p>
              <div className="price">
                {p.price} <small>/ Monat</small>
              </div>
              <ul>
                {p.features.map((f) => (
                  <li key={f}>
                    <Check />
                    {f}
                  </li>
                ))}
              </ul>
              <MagneticButton
                variant={p.featured ? "primary" : "ghost"}
                href={mailtoHref(
                  `Paket ${p.name} anfragen`,
                  `Hallo CleanLines Studio,\n\nich interessiere mich für das ${p.name}-Paket (${p.price} / Monat).\n\nBetrieb:\nBranche:\nStandort:\n\nViele Grüße`
                )}
              >
                {p.name} anfragen
              </MagneticButton>
            </div>
          ))}
        </div>
        <p className="price-note">
          Alle Pakete monatlich kündbar. Du behältst alle gelieferten Inhalte — auch nach einer Kündigung.
        </p>
      </div>
    </section>
  );
}
