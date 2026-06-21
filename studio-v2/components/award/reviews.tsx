"use client";

import { AnimatedHeading, CountUp, Marquee, Reveal } from "@/components/award/ux";
import { REVIEWS } from "@/lib/cl-data";

function ReviewCard({ text, name, role }: { text: string; name: string; role: string }) {
  return (
    <div className="w-[340px] shrink-0 rounded-[22px] border border-line bg-gradient-to-b from-surface to-bg-2 p-7">
      <div className="text-[15px] tracking-[3px] text-gold">&#9733;&#9733;&#9733;&#9733;&#9733;</div>
      <p className="my-4 text-[15.5px] leading-relaxed text-ink/90">&bdquo;{text}&ldquo;</p>
      <div className="flex items-center gap-3">
        <span className="grid h-9 w-9 place-items-center rounded-full bg-gradient-to-br from-gold to-gold-bright font-extrabold text-[#1a1206]">
          {name[0]}
        </span>
        <span className="text-dim">
          {name} &middot; {role}
        </span>
      </div>
    </div>
  );
}

export function AwReviews() {
  const cards = REVIEWS.map((r, i) => <ReviewCard key={i} text={r.text} name={r.name} role={r.role} />);

  return (
    <section className="py-24">
      <div className="mx-auto max-w-[1320px] px-5 sm:px-8">
        <span className="font-mono text-[12px] uppercase tracking-[0.2em] text-gold">Bewertungen</span>
        <AnimatedHeading
          as="h2"
          lines={["Betriebe, die nicht mehr", <span key="g" className="text-gold">planlos posten.</span>]}
          className="mt-5 font-display text-[clamp(34px,5.5vw,68px)] font-extrabold leading-[1.02] tracking-[-0.03em]"
        />
      </div>

      <div className="relative mt-14 space-y-5">
        <span
          aria-hidden
          className="pointer-events-none absolute inset-y-0 left-0 z-10 w-24 bg-gradient-to-r from-bg to-transparent"
        />
        <span
          aria-hidden
          className="pointer-events-none absolute inset-y-0 right-0 z-10 w-24 bg-gradient-to-l from-bg to-transparent"
        />
        <Marquee speed={48}>{cards}</Marquee>
        <Marquee speed={48} reverse>
          {cards}
        </Marquee>
      </div>

      <Reveal className="mt-12 text-center text-[15px] text-dim">
        <b className="font-display text-[20px] text-gold-bright">
          <CountUp value={4.9} decimals={1} />
        </b>{" "}
        / 5 &middot; &uuml;ber{" "}
        <b className="font-display text-[20px] text-gold-bright">
          <CountUp value={120} suffix="+" />
        </b>{" "}
        unterst&uuml;tzte Betriebe
      </Reveal>
    </section>
  );
}
