export function Marquee() {
  const a = ["CINEMATISCHE REELS", "KI-CONTENT", "GOOGLE-BEITRÄGE", "CONTENT-SYSTEM"];
  const b = ["SICHTBARKEIT", "VERTRAUEN", "MEHR ANFRAGEN", "PREMIUM-AUFTRITT"];
  const row = (arr: string[]) => [...arr, ...arr].map((x, i) => <span key={i}>{x}</span>);
  return (
    <div className="marquee" aria-hidden="true">
      <div className="mrow">{row(a)}</div>
      <div className="mrow rev">{row(b)}</div>
    </div>
  );
}
