import { nav } from "../../content/siteContent";
import { scrollToTarget } from "../../motion/lenis";

/** In-page section navigation driven by Lenis smooth scroll. */
export default function Navigation() {
  return (
    <nav className="nav" aria-label="Hauptnavigation">
      {nav.map((item) => (
        <button
          key={item.target}
          className="nav__item"
          data-cursor="hover"
          onClick={() => scrollToTarget(`#${item.target}`, -40)}
        >
          {item.label}
        </button>
      ))}
    </nav>
  );
}
