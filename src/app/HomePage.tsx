import { MARQUEE, mailtoHref, whatsappHref } from "../content/siteContent";
import { HeroSection } from "../components/sections/HeroSection";
import { DiagnosisSection } from "../components/sections/DiagnosisSection";
import { ContentOSSection } from "../components/sections/ContentOSSection";
import { ReelCinemaSection } from "../components/sections/ReelCinemaSection";
import { IndustriesSection } from "../components/sections/IndustriesSection";
import { TransformationSection } from "../components/sections/TransformationSection";
import { PipelineSection } from "../components/sections/PipelineSection";
import { PackagesSection } from "../components/sections/PackagesSection";
import { AddOnsSection } from "../components/sections/AddOnsSection";
import { TrustFAQSection } from "../components/sections/TrustFAQSection";
import { FinalCTASection } from "../components/sections/FinalCTASection";

function Marquee() {
  return (
    <div className="marquee" aria-hidden>
      <div className="marquee-track">
        {[...MARQUEE, ...MARQUEE].map((m, i) => (
          <div className="marquee-item" key={i}>
            {m}
          </div>
        ))}
      </div>
    </div>
  );
}

function Footer() {
  return (
    <footer className="site-footer">
      <div className="wrap footer-inner">
        <p>© 2026 CleanLines Studio — Cinematic Content Engine.</p>
        <div className="footer-links">
          <a href={mailtoHref("Kontakt")}>Kontakt</a>
          <a href={whatsappHref("Hallo CleanLines Studio")} target="_blank" rel="noopener noreferrer">
            WhatsApp
          </a>
          <a href="#" onClick={(e) => e.preventDefault()}>
            Impressum
          </a>
          <a href="#" onClick={(e) => e.preventDefault()}>
            Datenschutz
          </a>
        </div>
      </div>
    </footer>
  );
}

export function HomePage() {
  return (
    <main className="shell">
      <HeroSection />
      <Marquee />
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
      <Footer />
    </main>
  );
}
