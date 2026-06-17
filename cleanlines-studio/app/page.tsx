import { Preloader } from "@/components/ui/preloader";
import { Cursor } from "@/components/ui/cursor";
import { SoundLayer } from "@/components/ui/sound";
import { PageCurtain } from "@/components/ui/page-curtain";
import { ScrollBackdrop } from "@/components/ui/scroll-backdrop";
import { Divider } from "@/components/ui/divider";
import { Navigation } from "@/components/navigation";
import { Hero } from "@/components/hero";
import { Marquee } from "@/components/ui/marquee";
import { Diagnosis } from "@/components/diagnosis";
import { Transformation } from "@/components/transformation";
import { ReelCinema } from "@/components/reel-cinema";
import { CleanlinesOS } from "@/components/cleanlines-os";
import { Industries } from "@/components/industries";
import { Pipeline } from "@/components/pipeline";
import { Services } from "@/components/services";
import { ContentCompare } from "@/components/content-compare";
import { Pricing } from "@/components/pricing";
import { Faq } from "@/components/faq";
import { FinalCta } from "@/components/final-cta";
import { Footer } from "@/components/footer";

export default function Home() {
  return (
    <>
      <Preloader />
      <Cursor />
      <SoundLayer />
      <PageCurtain />
      <ScrollBackdrop />
      <Navigation />
      <main>
        <Hero />
        <Marquee />
        <Diagnosis />
        <Transformation />
        <ReelCinema />
        <CleanlinesOS />
        <Divider label="Branchen" />
        <Industries />
        <Pipeline />
        <Divider label="Leistungen" />
        <Services />
        <ContentCompare />
        <Pricing />
        <Faq />
        <FinalCta />
      </main>
      <Footer />
    </>
  );
}
