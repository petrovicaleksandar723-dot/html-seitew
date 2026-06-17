"use client";

import { useRef } from "react";
import { motion, useScroll, useTransform } from "framer-motion";
import { Reveal } from "@/components/ui/reveal";
import { AnimatedHeading } from "@/components/ui/animated-heading";
import { PIPELINE } from "@/lib/constants";

export function Pipeline() {
  const ref = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start 70%", "end 60%"],
  });
  const lineScale = useTransform(scrollYProgress, [0, 1], [0, 1]);

  return (
    <section id="pipeline" className="py-[clamp(90px,14vw,170px)]">
      <div className="shell content relative z-10">
        <div className="max-w-[680px]">
          <Reveal>
            <span className="eyebrow">Pipeline</span>
          </Reveal>
          <AnimatedHeading
            className="mt-6 font-display text-[clamp(32px,5vw,60px)] font-bold leading-[1.02] tracking-[-0.02em]"
            lines={[
              [{ t: "Von der Analyse zum" }],
              [{ t: "laufenden Content-System.", accent: true }],
            ]}
          />
          <Reveal delay={0.1}>
            <p className="mt-6 font-body text-[17px] leading-relaxed text-dim">
              Vom ersten Blick auf deinen Betrieb bis zum fertigen Content läuft
              alles klar, schnell und ohne komplizierte Agenturprozesse.
            </p>
          </Reveal>
        </div>

        <div ref={ref} className="relative mt-16 pl-8 md:pl-0">
          {/* progress rail */}
          <div className="absolute left-[7px] top-2 h-[calc(100%-1rem)] w-px bg-line md:left-1/2 md:-translate-x-1/2">
            <motion.div
              style={{ scaleY: lineScale }}
              className="h-full w-full origin-top bg-gradient-to-b from-gold-bright via-gold to-gold-deep"
            />
          </div>

          <div className="space-y-12">
            {PIPELINE.map((step, i) => (
              <Reveal key={step.n} delay={0.04}>
                <div
                  className={`relative md:grid md:grid-cols-2 md:gap-12 ${
                    i % 2 === 1 ? "md:[&>*:first-child]:order-2" : ""
                  }`}
                >
                  {/* node */}
                  <span className="absolute -left-[29px] top-2 h-3.5 w-3.5 rounded-full border-2 border-gold bg-bg shadow-[0_0_14px_2px_rgba(216,178,116,0.6)] md:left-1/2 md:-translate-x-1/2" />

                  <div
                    className={`${
                      i % 2 === 1 ? "md:text-left md:pl-12" : "md:text-right md:pr-12"
                    }`}
                  >
                    <span className="font-display text-[clamp(40px,6vw,72px)] font-extrabold leading-none text-transparent [-webkit-text-stroke:1px_rgba(216,178,116,0.5)]">
                      {step.n}
                    </span>
                  </div>

                  <div className={i % 2 === 1 ? "md:pr-12 md:text-right" : "md:pl-12"}>
                    <h3 className="font-display text-[22px] font-bold tracking-tight">
                      {step.title}
                    </h3>
                    <p className="mt-2 max-w-[420px] font-body text-[14.5px] leading-relaxed text-dim md:inline-block">
                      {step.body}
                    </p>
                  </div>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
