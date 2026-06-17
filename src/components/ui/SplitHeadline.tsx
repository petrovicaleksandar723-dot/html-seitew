import { useEffect, useRef } from "react";
import { revealHeadline } from "../../motion/splitText";
import { gsap } from "../../motion/scrollTriggers";

interface Props {
  text: string;
  as?: "h1" | "h2" | "h3";
  className?: string;
  /** Disable scroll trigger (used when an external timeline drives the reveal). */
  manual?: boolean;
}

/**
 * Headline that splits into masked words and reveals them with an upward slide
 * as it scrolls into view.
 */
export default function SplitHeadline({
  text,
  as = "h2",
  className = "headline-section",
  manual = false,
}: Props) {
  const ref = useRef<HTMLHeadingElement>(null);
  const Tag = as;

  useEffect(() => {
    const el = ref.current;
    if (!el || manual) return;
    const ctx = gsap.context(() => revealHeadline(el), el);
    return () => ctx.revert();
  }, [manual, text]);

  return (
    <Tag ref={ref} className={className}>
      {text}
    </Tag>
  );
}
