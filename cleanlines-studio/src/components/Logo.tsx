export function Logo({ className = "" }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 100 100" fill="none" stroke="currentColor" strokeWidth={3} strokeLinejoin="round" strokeLinecap="round" aria-hidden="true">
      <polygon points="50,6 88.1,28 88.1,72 50,94 11.9,72 11.9,28" />
      <polygon points="50,17 78.6,33.5 78.6,66.5 50,83 21.4,66.5 21.4,33.5" opacity={0.75} />
      <path d="M50,50 L50,6 M50,50 L11.9,72 M50,50 L88.1,72" />
    </svg>
  );
}
