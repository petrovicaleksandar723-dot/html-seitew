interface Props {
  vertical?: boolean;
  className?: string;
}

/** A thin gold gradient divider line. */
export default function GlowLine({ vertical = false, className = "" }: Props) {
  return <div className={`glow-line ${vertical ? "vertical" : ""} ${className}`} aria-hidden />;
}
