import { Hero } from "@/components/hero";
import { Manifesto } from "@/components/manifesto";
import { Services } from "@/components/services";
import { Industries } from "@/components/industries";
import { Process } from "@/components/process";
import { Pricing } from "@/components/pricing";
import { FinalCta } from "@/components/final-cta";
import { Footer } from "@/components/footer";

export default function Page() {
  return (
    <main>
      <Hero />
      <Manifesto />
      <Services />
      <Industries />
      <Process />
      <Pricing />
      <FinalCta />
      <Footer />
    </main>
  );
}
