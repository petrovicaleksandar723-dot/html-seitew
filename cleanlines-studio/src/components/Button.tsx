import type { ReactNode } from "react";
import { useMagnetic } from "../motion/useMagnetic";

type Props = {
  href: string;
  children: ReactNode;
  variant?: "primary" | "ghost" | "wa";
  external?: boolean;
  className?: string;
};

export function Button({ href, children, variant = "primary", external = false, className = "" }: Props) {
  const ref = useMagnetic<HTMLAnchorElement>(0.3);
  const ext = external ? { target: "_blank", rel: "noopener" } : {};
  return (
    <a ref={ref} className={`btn btn-${variant} ${className}`} href={href} {...ext}>
      {children}
    </a>
  );
}
