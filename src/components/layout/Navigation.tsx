import { NAV } from "../../content/siteContent";
import { scrollToId } from "../../motion/lenis";

export function Navigation({ onNavigate }: { onNavigate?: () => void }) {
  return (
    <>
      {NAV.map((n) => (
        <a
          key={n.id}
          href={`#${n.id}`}
          onClick={(e) => {
            e.preventDefault();
            scrollToId(n.id);
            onNavigate?.();
          }}
        >
          {n.label}
        </a>
      ))}
    </>
  );
}
