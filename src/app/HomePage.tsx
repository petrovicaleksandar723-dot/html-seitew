import { brand, brand as b, hero, contact, mailto, whatsapp, waMessage } from "../content/siteContent";
import BrandMark from "../components/ui/BrandMark";
import HeroSection from "../components/sections/HeroSection";
import DiagnosisSection from "../components/sections/DiagnosisSection";
import ContentOSSection from "../components/sections/ContentOSSection";
import ReelCinemaSection from "../components/sections/ReelCinemaSection";
import IndustriesSection from "../components/sections/IndustriesSection";
import TransformationSection from "../components/sections/TransformationSection";
import PipelineSection from "../components/sections/PipelineSection";
import PackagesSection from "../components/sections/PackagesSection";
import AddOnsSection from "../components/sections/AddOnsSection";
import TrustFAQSection from "../components/sections/TrustFAQSection";
import FinalCTASection from "../components/sections/FinalCTASection";

interface Props {
  ready: boolean;
}

/** The full cinematic scroll: twelve scenes assembled in order. */
export default function HomePage({ ready }: Props) {
  return (
    <main>
      <HeroSection ready={ready} />
      <DiagnosisSection />
      <ContentOSSection />
      <ReelCinemaSection />
      <IndustriesSection />
      <TransformationSection />
      <PipelineSection />
      <PackagesSection />
      <AddOnsSection />
      <TrustFAQSection />
      <FinalCTASection />

      <footer className="footer" id="kontakt">
        <div className="footer__top shell">
          <div className="footer__brandcol">
            <BrandMark />
            <p className="footer__tag">{b.tagline}. Content, der zeigt, warum Kunden sich für dich entscheiden.</p>
            <div className="footer__contact">
              <a href={mailto("Kostenlose Content-Preview")} data-cursor="hover">{hero.ctaPrimary}</a>
              <a href={whatsapp(waMessage)} target="_blank" rel="noopener noreferrer" data-cursor="hover">
                WhatsApp-Anfrage
              </a>
            </div>
          </div>
          <nav className="footer__nav" aria-label="Footer-Navigation">
            <span className="footer__navlabel">Navigation</span>
            <a href="#diagnosis">Diagnose</a>
            <a href="#content-os">System</a>
            <a href="#reel-cinema">Reel Cinema</a>
            <a href="#industries">Branchen</a>
            <a href="#packages">Pakete</a>
            <a href="#final-cta">Kontakt</a>
          </nav>
          <div className="footer__meta">
            <span className="footer__navlabel">Studio</span>
            <span>{contact.location}</span>
            <a href={mailto("Anfrage")}>{contact.email}</a>
          </div>
        </div>
        <div className="footer__bottom shell">
          <p>© {new Date().getFullYear()} {brand.name}. Alle Rechte vorbehalten.</p>
          <div className="footer__links">
            <a href="#impressum">Impressum</a>
            <a href="#datenschutz">Datenschutz</a>
          </div>
        </div>
      </footer>
    </main>
  );
}
