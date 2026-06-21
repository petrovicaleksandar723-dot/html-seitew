"use client";

import { motion, useReducedMotion } from "framer-motion";
import {
  Reveal,
  AnimatedHeading,
  Eyebrow,
  CountUp,
  stagger,
} from "@/components/cl/ui";
import { REVIEWS } from "@/lib/cl-data";

export function ClReviews() {
  const reduce = useReducedMotion();

  return (
    <section className="relative px-5 py-16">
      <div className="mx-auto w-full max-w-[600px]">
        <Eyebrow>Bewertungen</Eyebrow>

        <AnimatedHeading
          as="h2"
          delay={0.05}
          className="mt-5 font-display text-[clamp(28px,8vw,42px)] font-extrabold leading-[1.08] tracking-[-0.025em]"
          lines={[
            <>Betriebe, die nicht mehr</>,
            <>
              planlos <span className="text-gold">posten.</span>
            </>,
          ]}
        />

        <div className="mt-7 flex flex-col gap-3.5">
          {REVIEWS.map((review, i) => (
            <motion.article
              key={review.name}
              {...stagger(i)}
              whileHover={reduce ? undefined : { y: -5 }}
              transition={{ type: "spring", stiffness: 300, damping: 22 }}
              className="rounded-[18px] border border-line bg-gradient-to-b from-surface to-bg-2 p-5"
            >
              <div className="text-[15px] tracking-[3px] text-gold">★★★★★</div>
              <p className="my-3 text-[15px] text-[#e7e3da]">„{review.text}“</p>
              <div className="flex items-center gap-2.5 text-[13.5px] font-semibold text-dim">
                <span className="grid h-[34px] w-[34px] place-items-center rounded-full bg-gradient-to-br from-gold to-gold-bright text-[#1a1206] font-extrabold">
                  {review.name[0]}
                </span>
                {review.name} · {review.role}
              </div>
            </motion.article>
          ))}
        </div>

        <Reveal className="mt-6 text-center text-[14px] text-dim">
          <b className="font-display text-[18px] text-gold-bright">
            <CountUp value={4.9} decimals={1} />
          </b>{" "}
          / 5 · über{" "}
          <b className="font-display text-[18px] text-gold-bright">
            <CountUp value={120} />
          </b>{" "}
          unterstützte Betriebe
        </Reveal>
      </div>
    </section>
  );
}
