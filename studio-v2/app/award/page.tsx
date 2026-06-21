import type { Metadata } from "next";
import { AwardNav } from "@/components/award/nav";
import { ScrollProgress } from "@/components/award/ux";
import { AwHero } from "@/components/award/hero";
import { AwLogos } from "@/components/award/logos";
import { AwServices } from "@/components/award/services";
import { AwShowreel } from "@/components/award/showreel";
import { AwBranchen } from "@/components/award/branchen";
import { AwEditorial } from "@/components/award/editorial";
import { AwBeforeAfter } from "@/components/award/before-after";
import { AwPricing } from "@/components/award/pricing";
import { AwEinzel } from "@/components/award/einzel";
import { AwReviews } from "@/components/award/reviews";
import { AwFaq } from "@/components/award/faq";
import { AwFinalCta } from "@/components/award/final-cta";
import { AwFooter } from "@/components/award/footer";

export const metadata: Metadata = {
  title: "CleanLines Studio — Content, der deinen Betrieb sichtbar macht",
  description:
    "Jeden Monat fertige Reel-Ideen, Captions, Google-Beiträge und ein klarer Content-Plan – passend zu deinem Betrieb. Award-Level Content-Studio für lokale Betriebe.",
};

export default function AwardPage() {
  return (
    <>
      <div
        aria-hidden
        className="pointer-events-none fixed inset-0 -z-10"
        style={{
          background:
            "radial-gradient(70% 50% at 50% -8%, rgba(216,178,116,0.15), transparent 70%), radial-gradient(45% 35% at 100% 100%, rgba(216,178,116,0.06), transparent 70%), #060504",
        }}
      />
      <ScrollProgress />
      <AwardNav />
      <main id="top" className="relative">
        <AwHero />
        <AwLogos />
        <AwServices />
        <AwShowreel />
        <AwBranchen />
        <AwEditorial />
        <AwBeforeAfter />
        <AwPricing />
        <AwEinzel />
        <AwReviews />
        <AwFaq />
        <AwFinalCta />
        <AwFooter />
      </main>
    </>
  );
}
