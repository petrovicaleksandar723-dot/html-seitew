"use client";

import { useRef, useState } from "react";
import { motion, useReducedMotion } from "framer-motion";
import {
  Reveal,
  AnimatedHeading,
  stagger,
  SPRING,
  EASE_OUT,
  useHoverCapable,
} from "@/components/award/ux";
import { Icon } from "@/components/cl/icons";
import { SERVICES } from "@/lib/cl-data";

function ServiceCard({
  item,
  i,
  featured,
}: {
  item: (typeof SERVICES)[number];
  i: number;
  featured: boolean;
}) {
  const hover = useHoverCapable();
  const reduce = useReducedMotion();
  const ref = useRef<HTMLDivElement>(null);
  const [glow, setGlow] = useState<{ x: number; y: number } | null>(null);

  const showGlow = hover && !reduce;

  return (
    <motion.div
      {...stagger(i)}
      className={featured ? "lg:col-span-2 lg:row-span-1" : ""}
    >
      <motion.article
        ref={ref}
        whileHover={showGlow ? { y: -6 } : undefined}
        transition={SPRING}
        onPointerMove={(e) => {
          if (!showGlow) return;
          const r = ref.current?.getBoundingClientRect();
          if (!r) return;
          setGlow({ x: e.clientX - r.left, y: e.clientY - r.top });
        }}
        onPointerLeave={() => setGlow(null)}
        className={`group relative h-full cursor-pointer overflow-hidden rounded-[22px] border border-line bg-gradient-to-b from-surface to-bg-2 p-7 transition-colors duration-300 hover:border-gold/30 md:p-8 ${
          featured ? "md:p-10" : ""
        }`}
      >
        {/* cursor-follow gold radial glow (desktop only) */}
        {showGlow && (
          <motion.span
            aria-hidden
            className="pointer-events-none absolute h-[340px] w-[340px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-[radial-gradient(circle,rgba(216,178,116,0.16),transparent_70%)]"
            initial={false}
            animate={{ opacity: glow ? 1 : 0 }}
            transition={{ duration: 0.25, ease: EASE_OUT }}
            style={{ left: glow?.x ?? 0, top: glow?.y ?? 0 }}
          />
        )}

        {/* faint background flourish on featured */}
        {featured && (
          <span
            aria-hidden
            className="pointer-events-none absolute -right-16 -top-16 h-56 w-56 rounded-full bg-[radial-gradient(circle,rgba(216,178,116,0.10),transparent_70%)] blur-xl"
          />
        )}

        {/* corner index */}
        <span className="absolute right-7 top-7 font-mono text-[12px] text-muted">
          /{String(i + 1).padStart(2, "0")}
        </span>

        <div className="relative z-10 flex h-full flex-col">
          <div
            className={`grid place-items-center rounded-2xl border border-gold/30 bg-gold/[0.12] text-gold-bright transition-transform duration-300 ease-out group-hover:scale-105 group-hover:-rotate-3 ${
              featured ? "h-14 w-14" : "h-12 w-12"
            }`}
          >
            <Icon
              name={item.icon as never}
              className={featured ? "h-7 w-7" : "h-6 w-6"}
            />
          </div>

          <h3
            className={`mt-6 font-display font-bold leading-tight ${
              featured
                ? "text-[clamp(24px,2.4vw,34px)]"
                : "text-[clamp(19px,1.6vw,24px)]"
            }`}
          >
            {item.title}
          </h3>

          <p
            className={`mt-3 text-dim leading-relaxed ${
              featured ? "max-w-[460px] text-[16px]" : "text-[15px]"
            }`}
          >
            {item.body}
          </p>
        </div>
      </motion.article>
    </motion.div>
  );
}

export function AwServices() {
  return (
    <section
      id="leistungen"
      className="relative mx-auto max-w-[1320px] px-5 py-24 sm:px-8 md:py-32"
    >
      <div className="font-mono text-[12px] uppercase tracking-[0.2em] text-gold">
        01 — Leistungen
      </div>

      <AnimatedHeading
        as="h2"
        lines={[
          "Alles vorbereitet.",
          <span key="g" className="text-gold">
            Du musst nur noch posten.
          </span>,
        ]}
        className="mt-5 font-display text-[clamp(34px,5.5vw,68px)] font-extrabold leading-[1.02] tracking-[-0.03em]"
      />

      <Reveal delay={0.1}>
        <p className="mt-6 max-w-[560px] text-[clamp(15px,1.2vw,17px)] text-dim">
          Ideen, Texte und ein klarer Plan – fertig vorbereitet für deinen
          Betrieb. Du veröffentlichst nur noch und wirkst sofort aktiver.
        </p>
      </Reveal>

      <div className="mt-14 grid gap-5 md:grid-cols-2 lg:grid-cols-3">
        {SERVICES.map((item, i) => (
          <ServiceCard key={item.title} item={item} i={i} featured={i === 0} />
        ))}
      </div>
    </section>
  );
}
