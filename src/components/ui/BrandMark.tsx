import { brand } from "../../content/siteContent";

interface Props {
  className?: string;
  withWord?: boolean;
}

/**
 * Cleanlines monogram: three "clean lines" of decreasing width forming an
 * abstract editorial mark, optionally paired with the wordmark.
 */
export default function BrandMark({ className = "", withWord = true }: Props) {
  return (
    <span className={`brandmark ${className}`}>
      <svg viewBox="0 0 40 28" width="34" height="24" aria-hidden focusable="false">
        <defs>
          <linearGradient id="bm-g" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0" stopColor="#f4d7a1" />
            <stop offset="1" stopColor="#d6a65f" />
          </linearGradient>
        </defs>
        <g stroke="url(#bm-g)" strokeWidth="2.4" strokeLinecap="round">
          <line x1="3" y1="6" x2="37" y2="6" />
          <line x1="3" y1="14" x2="28" y2="14" />
          <line x1="3" y1="22" x2="19" y2="22" />
        </g>
      </svg>
      {withWord && <span className="brandmark__word">{brand.name}</span>}
    </span>
  );
}
