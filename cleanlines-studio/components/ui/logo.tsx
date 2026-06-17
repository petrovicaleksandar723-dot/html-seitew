type Props = {
  className?: string;
  withWordmark?: boolean;
};

/**
 * CLEANLINES STUDIOS — gold hexagonal emblem, recreated as crisp vector
 * (nested flat-top hexagons + 3D fold). Swap for the exact brand asset by
 * dropping a PNG/SVG into /public and replacing this component's markup.
 */
export function LogoMark({ className = "" }: { className?: string }) {
  return (
    <svg viewBox="0 0 100 100" className={className} fill="none" aria-hidden="true">
      <defs>
        <linearGradient id="cl-gold" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#f7dca6" />
          <stop offset="45%" stopColor="#d8b274" />
          <stop offset="100%" stopColor="#9c7235" />
        </linearGradient>
      </defs>

      {/* outer hexagon */}
      <path
        d="M8 50 L29 13.6 L71 13.6 L92 50 L71 86.4 L29 86.4 Z"
        stroke="url(#cl-gold)"
        strokeWidth="2.2"
        strokeLinejoin="round"
      />
      {/* middle hexagon */}
      <path
        d="M16 50 L33 20.6 L67 20.6 L84 50 L67 79.4 L33 79.4 Z"
        stroke="url(#cl-gold)"
        strokeWidth="1.5"
        strokeLinejoin="round"
        opacity="0.8"
      />
      {/* inner hexagon */}
      <path
        d="M24 50 L37 27.5 L63 27.5 L76 50 L63 72.5 L37 72.5 Z"
        stroke="url(#cl-gold)"
        strokeWidth="1.2"
        strokeLinejoin="round"
        opacity="0.6"
      />
      {/* 3D fold — three spokes 120° apart */}
      <path
        d="M50 50 L29 13.6 M50 50 L84 50 M50 50 L37 79.4"
        stroke="url(#cl-gold)"
        strokeWidth="1.5"
        strokeLinecap="round"
        opacity="0.95"
      />
    </svg>
  );
}

export function Logo({ className = "", withWordmark = true }: Props) {
  return (
    <span className={`inline-flex items-center gap-3 ${className}`}>
      <LogoMark className="h-9 w-9 drop-shadow-[0_2px_14px_rgba(216,178,116,0.5)]" />
      {withWordmark && (
        <span className="flex flex-col leading-none">
          <span className="font-display text-[15px] font-medium tracking-[0.3em] text-ink">
            CLEANLINES
          </span>
          <span className="mt-1 font-mono text-[8.5px] tracking-[0.5em] text-gold/80">
            STUDIOS
          </span>
        </span>
      )}
    </span>
  );
}
