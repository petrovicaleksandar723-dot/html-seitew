export function SectionNumber({ n }: { n: string }) {
  return (
    <span className="section-num" aria-hidden>
      {n}
    </span>
  );
}
