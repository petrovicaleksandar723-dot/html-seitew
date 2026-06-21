"use client";

import { useRef } from "react";
import {
  motion,
  useMotionValue,
  useReducedMotion,
  useTransform,
  type MotionValue,
} from "framer-motion";
import { Reveal, AnimatedHeading, Eyebrow } from "@/components/cl/ui";
import { Icon } from "@/components/cl/icons";
import type { IconName } from "@/components/cl/icons";
import { SERVICES } from "@/lib/cl-data";

/* radial glow that follows the pointer (transform/opacity-only animation) */
function useMotionTemplateGlow(mx: MotionValue<number>, my: MotionValue<number>) {
  return useTransform(
    [mx, my],
    ([x, y]: number[]) =>
      `radial-gradient(180px 180px at ${x}% ${y}%, rgba(216,178,116,0.16), transparent 70%)`
  );
}

function ServiceCard({
  service,
  index,
}: {
  service: (typeof SERVICES)[number];
  index: number;
}) {
  const reduce = useReducedMotion();
  const ref = useRef<HTMLDivElement>(null);
  const mx = useMotionValue(50);
  const my = useMotionValue(50);

  return (
    <motion.div
      ref={ref}
      initial={reduce ? false : { opacity: 0, y: 22 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-8% 0px" }}
      transition={{ duration: 0.7, delay: index * 0.07, ease: [0.16, 1, 0.3, 1] }}
      whileHover={reduce ? undefined : { y: -4 }}
      onPointerMove={(e) => {
        if (reduce) return;
        const r = ref.current?.getBoundingClientRect();
        if (!r) return;
        mx.set(((e.clientX - r.left) / r.width) * 100);
        my.set(((e.clientY - r.top) / r.height) * 100);
      }}
      className="group relative overflow-hidden rounded-[18px] border border-line bg-gradient-to-b from-surface to-bg-2 p-5 transition-colors hover:border-gold/30"
    >
      {/* cursor-follow champagne glow */}
      <motion.span
        aria-hidden
        style={{
          background: useMotionTemplateGlow(mx, my),
        }}
        className="pointer-events-none absolute inset-0 opacity-0 transition-opacity duration-300 group-hover:opacity-100"
      />

      <div className="relative">
        <div className="grid h-[46px] w-[46px] place-items-center rounded-[13px] border border-gold/30 bg-gold/[0.12] text-gold-bright transition-transform duration-500 ease-out-expo group-hover:-rotate-6 group-hover:scale-110">
          <Icon name={service.icon as IconName} className="h-6 w-6" />
        </div>

        <h3 className="mt-3.5 font-display text-[18px] font-bold">
          {service.title}
        </h3>
        <p className="mt-1.5 text-[14.5px] leading-relaxed text-dim">
          {service.body}
        </p>
      </div>
    </motion.div>
  );
}

export function ClServices() {
  return (
    <section id="leistungen" className="relative px-5 py-16">
      <div className="mx-auto w-full max-w-[600px]">
        <Eyebrow>Leistungen</Eyebrow>

        <AnimatedHeading
          as="h2"
          delay={0.05}
          className="mt-5 font-display text-[clamp(28px,8vw,42px)] font-extrabold leading-[1.08] tracking-[-0.025em]"
          lines={[
            "Alles vorbereitet.",
            <span key="line2">
              Du musst nur noch <span className="text-gold">posten.</span>
            </span>,
          ]}
        />

        <Reveal delay={0.15} className="mt-7">
          <div className="flex flex-col gap-3.5">
            {SERVICES.map((service, i) => (
              <ServiceCard key={service.title} service={service} index={i} />
            ))}
          </div>
        </Reveal>
      </div>
    </section>
  );
}
