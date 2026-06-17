interface Props {
  num: string;
  label?: string;
}

/** Technical scene index marker, e.g. "03 / Diagnose". */
export default function SectionNumber({ num, label }: Props) {
  return (
    <span className="section-number">
      {num}
      {label ? ` / ${label}` : ""}
    </span>
  );
}
