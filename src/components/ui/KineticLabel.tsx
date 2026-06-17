interface Props {
  text: string;
  className?: string;
}

/** A technical mono label rendered per-character for kinetic styling. */
export default function KineticLabel({ text, className = "" }: Props) {
  return (
    <span className={`kinetic-label ${className}`} aria-label={text}>
      {text.split("").map((ch, i) => (
        <span key={i} style={{ transitionDelay: `${i * 12}ms` }}>
          {ch === " " ? " " : ch}
        </span>
      ))}
    </span>
  );
}
