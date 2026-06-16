import { ReactNode } from "react";

export function KineticLabel({
  children,
  faint,
  reverse,
  className = "",
}: {
  children: ReactNode;
  faint?: boolean;
  reverse?: boolean;
  className?: string;
}) {
  return (
    <span className={`klabel ${faint ? "faint" : ""} ${reverse ? "r" : ""} ${className}`} data-fade>
      {children}
    </span>
  );
}
