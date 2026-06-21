import type { Metadata } from "next";
import { ClHeader } from "@/components/cl/header";
import { Intro } from "@/components/cl/intro";
import { ClHero } from "@/components/cl/hero";
import { ClServices } from "@/components/cl/services";
import { ClShowreel } from "@/components/cl/showreel";
import { ClBranchen } from "@/components/cl/branchen";
import { ClEditorial } from "@/components/cl/editorial";
import { ClBeforeAfter } from "@/components/cl/before-after";
import { ClPricing } from "@/components/cl/pricing";
import { ClEinzel } from "@/components/cl/einzel";
import { ClReviews } from "@/components/cl/reviews";
import { ClFaq } from "@/components/cl/faq";
import { ClFinalCta } from "@/components/cl/final-cta";
import { ClFooter } from "@/components/cl/footer";

export const metadata: Metadata = {
  title: "CleanLines Studio — Content für lokale Betriebe",
  description:
    "Jeden Monat fertige Reel-Ideen, Captions, Google-Beiträge und ein klarer Content-Plan – passend zu deinem Betrieb.",
};

export default function StudioPage() {
  return (
    <>
      {/* static brand backdrop glow */}
      <div
        aria-hidden
        className="pointer-events-none fixed inset-0 -z-10"
        style={{
          background:
            "radial-gradient(60% 40% at 50% -5%, rgba(216,178,116,0.16), transparent 70%), radial-gradient(50% 35% at 100% 100%, rgba(216,178,116,0.07), transparent 70%), #060504",
        }}
      />
      <ClHeader />
      <main id="top">
        <Intro />
        <div className="relative z-40 bg-bg">
          <ClHero />
          <ClServices />
          <ClShowreel />
          <ClBranchen />
          <ClEditorial />
          <ClBeforeAfter />
          <ClPricing />
          <ClEinzel />
          <ClReviews />
          <ClFaq />
          <ClFinalCta />
          <ClFooter />
        </div>
      </main>
    </>
  );
}
