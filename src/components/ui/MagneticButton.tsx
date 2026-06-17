import { useRef, type ReactNode, type MouseEvent, type RefObject } from "react";
import gsap from "gsap";

interface Props {
  children: ReactNode;
  href?: string;
  onClick?: () => void;
  variant?: "primary" | "ghost";
  external?: boolean;
  className?: string;
  ariaLabel?: string;
}

/**
 * Button/link with a magnetic hover: the element eases toward the cursor and
 * settles back with an elastic release. Works as <a> or <button>.
 */
export default function MagneticButton({
  children,
  href,
  onClick,
  variant = "primary",
  external,
  className = "",
  ariaLabel,
}: Props) {
  const ref = useRef<HTMLElement>(null);

  const handleMove = (e: MouseEvent) => {
    const el = ref.current;
    if (!el) return;
    const rect = el.getBoundingClientRect();
    const x = e.clientX - (rect.left + rect.width / 2);
    const y = e.clientY - (rect.top + rect.height / 2);
    gsap.to(el, { x: x * 0.32, y: y * 0.4, duration: 0.6, ease: "power3.out" });
  };

  const handleLeave = () => {
    if (ref.current)
      gsap.to(ref.current, { x: 0, y: 0, duration: 0.8, ease: "elastic.out(1, 0.4)" });
  };

  const cls = `btn btn-${variant} ${className}`;
  const inner = <span>{children}</span>;

  if (href) {
    return (
      <a
        ref={ref as RefObject<HTMLAnchorElement>}
        href={href}
        className={cls}
        aria-label={ariaLabel}
        onMouseMove={handleMove}
        onMouseLeave={handleLeave}
        data-cursor="hover"
        {...(external ? { target: "_blank", rel: "noopener noreferrer" } : {})}
      >
        {inner}
      </a>
    );
  }

  return (
    <button
      ref={ref as RefObject<HTMLButtonElement>}
      className={cls}
      aria-label={ariaLabel}
      onClick={onClick}
      onMouseMove={handleMove}
      onMouseLeave={handleLeave}
      data-cursor="hover"
    >
      {inner}
    </button>
  );
}
