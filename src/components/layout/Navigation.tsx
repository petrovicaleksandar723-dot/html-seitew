import { useEffect, useState } from "react";
import { nav } from "../../content/siteContent";
import { scrollToTarget } from "../../motion/lenis";

/** In-page section navigation with scroll-spy active state. */
export default function Navigation() {
  const [active, setActive] = useState<string>(nav[0].target);

  useEffect(() => {
    const sections = nav
      .map((n) => document.getElementById(n.target))
      .filter((el): el is HTMLElement => !!el);
    if (!sections.length) return;

    const io = new IntersectionObserver(
      (entries) => {
        // pick the entry nearest the top that is sufficiently in view
        const visible = entries
          .filter((e) => e.isIntersecting)
          .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
        if (visible[0]) setActive(visible[0].target.id);
      },
      { rootMargin: "-45% 0px -45% 0px", threshold: 0 }
    );
    sections.forEach((s) => io.observe(s));
    return () => io.disconnect();
  }, []);

  return (
    <nav className="nav" aria-label="Hauptnavigation">
      {nav.map((item) => (
        <button
          key={item.target}
          className={`nav__item ${active === item.target ? "is-active" : ""}`}
          data-cursor="hover"
          aria-current={active === item.target ? "true" : undefined}
          onClick={() => scrollToTarget(`#${item.target}`, -40)}
        >
          {item.label}
        </button>
      ))}
    </nav>
  );
}
