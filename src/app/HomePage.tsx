import { brand } from "../content/siteContent";
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

      <footer className="footer">
        <p>© {new Date().getFullYear()} {brand.name}. Alle Rechte vorbehalten.</p>
        <div className="footer__links">
          <a href="#impressum">Impressum</a>
          <a href="#datenschutz">Datenschutz</a>
          <a href="#final-cta">Kontakt</a>
        </div>
      </footer>
    </main>
  );
}
