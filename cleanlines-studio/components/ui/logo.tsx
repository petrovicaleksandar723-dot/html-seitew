type Props = {
  className?: string;
  withWordmark?: boolean;
};

/**
 * CLEANLINES STUDIOS — gold hexagonal emblem, recreated as crisp vector.
 * Swap for the exact brand file by replacing the <svg> paths if needed.
 */
export function LogoMark({ className = "" }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 100 100"
      className={className}
      fill="none"
      aria-hidden="true"
    >
      <defs>
        <linearGradient id="cl-gold" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#f4d79e" />
          <stop offset="50%" stopColor="#d8b274" />
          <stop offset="100%" stopColor="#a87f3e" />
        </linearGradient>
      </defs>
      {/* outer hexagon (flat-top) */}
      <path
        d="M50 6 L88 28 L88 72 L50 94 L12 72 L12 28 Z"
        stroke="url(#cl-gold)"
        strokeWidth="2.4"
        strokeLinejoin="round"
      />
      {/* inner hexagon */}
      <path
        d="M50 20 L76 35 L76 65 L50 80 L24 65 L24 35 Z"
        stroke="url(#cl-gold)"
        strokeWidth="1.6"
        strokeLinejoin="round"
        opacity="0.75"
      />
      {/* folded ribbon motif */}
      <path
        d="M50 20 L50 50 L24 65 M50 50 L76 35 M50 50 L50 80"
        stroke="url(#cl-gold)"
        strokeWidth="1.6"
        strokeLinejoin="round"
        strokeLinecap="round"
        opacity="0.9"
      />
    </svg>
  );
}

export function Logo({ className = "", withWordmark = true }: Props) {
  return (
    <span className={`inline-flex items-center gap-3 ${className}`}>
      <LogoMark className="h-9 w-9 drop-shadow-[0_2px_12px_rgba(216,178,116,0.45)]" />
      {withWordmark && (
        <span className="flex flex-col leading-none">
          <span className="font-display text-[17px] font-extrabold tracking-[0.12em] text-ink">
            CLEANLINES
          </span>
          <span className="font-mono text-[9px] tracking-[0.42em] text-gold/80">
            STUDIOS
          </span>
        </span>
      )}
    </span>
  );
}
