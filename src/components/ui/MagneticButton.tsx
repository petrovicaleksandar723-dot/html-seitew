import { useEffect, useRef, ReactNode, MouseEvent } from "react";
import { scrollToId } from "../../motion/lenis";

type Props = {
  children: ReactNode;
  variant?: "primary" | "ghost" | "wa";
  className?: string;
  href?: string;
  to?: string;
  onClick?: () => void;
  target?: string;
  rel?: string;
};

export function MagneticButton({
  children,
  variant = "primary",
  className = "",
  href,
  to,
  onClick,
  target,
  rel,
}: Props) {
  const ref = useRef<HTMLAnchorElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    if (!window.matchMedia("(pointer:fine) and (min-width:1024px)").matches) return;
    const move = (e: globalThis.MouseEvent) => {
      const r = el.getBoundingClientRect();
      el.style.transform = `translate(${(e.clientX - r.left - r.width / 2) * 0.3}px,${
        (e.clientY - r.top - r.height / 2) * 0.4
      }px)`;
    };
    const leave = () => {
      el.style.transform = "translate(0,0)";
    };
    el.addEventListener("mousemove", move);
    el.addEventListener("mouseleave", leave);
    return () => {
      el.removeEventListener("mousemove", move);
      el.removeEventListener("mouseleave", leave);
    };
  }, []);

  const handle = (e: MouseEvent) => {
    if (to) {
      e.preventDefault();
      scrollToId(to);
    }
    onClick?.();
  };

  return (
    <a
      ref={ref}
      href={href ?? (to ? `#${to}` : undefined)}
      className={`btn btn-${variant} mag ${className}`}
      onClick={handle}
      target={target}
      rel={rel}
    >
      {children}
    </a>
  );
}
