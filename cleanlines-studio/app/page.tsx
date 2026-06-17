import { Navigation } from "@/components/navigation";
import { Hero } from "@/components/hero";
import { Diagnosis } from "@/components/diagnosis";
import { Transformation } from "@/components/transformation";
import { ReelCinema } from "@/components/reel-cinema";
import { CleanlinesOS } from "@/components/cleanlines-os";
import { Industries } from "@/components/industries";
import { Pipeline } from "@/components/pipeline";
import { Services } from "@/components/services";
import { Pricing } from "@/components/pricing";
import { Faq } from "@/components/faq";
import { FinalCta } from "@/components/final-cta";
import { Footer } from "@/components/footer";

export default function Home() {
  return (
    <>
      <Navigation />
      <main>
        <Hero />
        <Diagnosis />
        <Transformation />
        <ReelCinema />
        <CleanlinesOS />
        <Industries />
        <Pipeline />
        <Services />
        <Pricing />
        <Faq />
        <FinalCta />
      </main>
      <Footer />
    </>
  );
}
