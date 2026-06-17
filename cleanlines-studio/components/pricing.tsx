"use client";

import { useRef } from "react";
import { useReducedMotion } from "framer-motion";
import { Reveal } from "@/components/ui/reveal";
import { AnimatedHeading } from "@/components/ui/animated-heading";
import { MediaBackdrop } from "@/components/ui/media-backdrop";
import { PLANS } from "@/lib/constants";
import { asset } from "@/lib/asset";

const BG = [asset("/videos/brand-gold-flow.mp4"), asset("/videos/brand-particles.mp4")];

type Plan = (typeof PLANS)[number];

function PlanCard({ plan, index }: { plan: Plan; index: number }) {
  const reduce = useReducedMotion();
  const ref = useRef<HTMLDivElement>(null);

  const onMove = (e: React.MouseEvent) => {
    if (!ref.current) return;
    const r = ref.current.getBoundingClientRect();
    const px = (e.clientX - r.left) / r.width;
    const py = (e.clientY - r.top) / r.height;
    // cursor-follow glow
    ref.current.style.setProperty("--mx", `${px * 100}%`);
    ref.current.style.setProperty("--my", `${py * 100}%`);
    if (reduce) return;
    // 3D tilt
    ref.current.style.transform = `perspective(1000px) rotateY(${(px - 0.5) * 8}deg) rotateX(${-(py - 0.5) * 8}deg) translateY(-6px)`;
  };
  const onLeave = () => {
    if (ref.current) ref.current.style.transform = "";
  };

  return (
    <Reveal delay={index * 0.07} className="h-full">
      <div
        ref={ref}
        onMouseMove={onMove}
        onMouseLeave={onLeave}
        className={`group relative flex h-full flex-col rounded-2xl p-8 transition-[transform,border-color,box-shadow] duration-300 ease-out-expo will-change-transform ${
          plan.featured
            ? "glass border-gold/40 shadow-[0_30px_80px_-30px_rgba(216,178,116,0.5)]"
            : "border border-line bg-bg/40 backdrop-blur-md hover:border-gold/30"
        }`}
        style={{ transformStyle: "preserve-3d" }}
      >
        {/* cursor-follow glow */}
        <div
          className="pointer-events-none absolute inset-0 rounded-2xl opacity-0 transition-opacity duration-300 group-hover:opacity-100"
          style={{
            background:
              "radial-gradient(420px circle at var(--mx,50%) var(--my,0%), rgba(216,178,116,0.16), transparent 60%)",
          }}
        />

        {plan.featured && (
          <span className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-gradient-to-br from-gold-bright to-gold-deep px-4 py-1 font-mono text-[10px] uppercase tracking-[0.15em] text-[#1a1206]">
            Beliebt
          </span>
        )}

        <div className="relative">
          <div className="font-mono text-[12px] uppercase tracking-[0.18em] text-muted">
            {plan.name}
          </div>
          <div className="mt-4 flex items-baseline gap-1">
            <span className="font-display text-[44px] font-extrabold tracking-[-0.03em]">
              {plan.price}
            </span>
            <span className="font-body text-[14px] text-muted">
              {plan.cadence}
            </span>
          </div>
          <p className="mt-3 min-h-[60px] font-body text-[13.5px] leading-relaxed text-dim">
            {plan.blurb}
          </p>

          <ul className="mt-6 flex-1 space-y-3 border-t border-line pt-6">
            {plan.features.map((f) => (
              <li
                key={f}
                className="flex items-start gap-3 font-body text-[13.5px] text-dim"
              >
                <span className="mt-0.5 text-gold">✓</span>
                {f}
              </li>
            ))}
          </ul>

          <a
            href="#kontakt"
            className={`mt-8 inline-flex w-full items-center justify-center rounded-full px-6 py-3.5 font-display text-[14px] font-bold transition-transform duration-300 hover:scale-[1.02] ${
              plan.featured
                ? "bg-gradient-to-br from-gold-bright to-gold-deep text-[#1a1206] shadow-[0_14px_40px_-12px_rgba(216,178,116,0.7)]"
                : "border border-white/20 text-ink hover:border-white/40"
            }`}
          >
            {plan.cta}
          </a>
        </div>
      </div>
    </Reveal>
  );
}

export function Pricing() {
  return (
    <section id="pakete" className="py-[clamp(90px,14vw,170px)]">
      <MediaBackdrop videos={BG} opacity={0.2} />
      <div className="lightfield left-1/2 top-1/3 z-[1] h-[36vw] w-[36vw] -translate-x-1/2 bg-gold/[0.05]" />
      <div className="shell content relative z-10">
        <div className="mx-auto max-w-[720px] text-center">
          <Reveal>
            <span className="eyebrow justify-center">Pakete</span>
          </Reveal>
          <AnimatedHeading
            className="mt-6 font-display text-[clamp(32px,5vw,56px)] font-bold leading-[1.04] tracking-[-0.02em]"
            lines={[
              [{ t: "Wähle, wie sichtbar dein Betrieb" }],
              [{ t: "werden soll.", accent: true }],
            ]}
          />
          <Reveal delay={0.1}>
            <p className="mx-auto mt-6 max-w-[520px] font-body text-[16px] leading-relaxed text-dim">
              Drei klare Pakete — je nachdem, ob du starten, wachsen oder deinen
              Auftritt auf Premium-Niveau bringen willst.
            </p>
          </Reveal>
        </div>

        <div className="mt-16 grid items-stretch gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {PLANS.map((plan, i) => (
            <PlanCard key={plan.name} plan={plan} index={i} />
          ))}
        </div>
      </div>
    </section>
  );
}
