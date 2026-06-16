export function GlowLine({ className = "" }: { className?: string }) {
  return (
    <span
      aria-hidden
      className={className}
      style={{
        display: "block",
        height: 1,
        background: "linear-gradient(90deg,var(--gold-2),transparent)",
      }}
    />
  );
}
