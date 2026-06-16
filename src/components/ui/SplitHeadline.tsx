import { ElementType } from "react";

/** Renders a headline with an optional gold-gradient phrase. The actual
 *  word-mask animation is applied by useScrollReveal via the [data-split] hook. */
export function SplitHeadline({
  text,
  gold,
  className = "h-section",
  as = "h2",
}: {
  text: string;
  gold?: string;
  className?: string;
  as?: ElementType;
}) {
  const Tag = as;
  let html = text;
  if (gold && text.includes(gold)) {
    const idx = text.lastIndexOf(gold);
    html = `${text.slice(0, idx)}<span class="gold-text">${gold}</span>${text.slice(idx + gold.length)}`;
  }
  return <Tag className={className} data-split dangerouslySetInnerHTML={{ __html: html }} />;
}
