import { brand } from "../../content/siteContent";
import { scrollToTarget } from "../../motion/lenis";
import Navigation from "./Navigation";

/** Fixed header with brand mark and section navigation. */
export default function Header() {
  return (
    <header className="header">
      <button
        className="header__brand"
        data-cursor="hover"
        onClick={() => scrollToTarget("#hero")}
        aria-label={`${brand.name} — nach oben`}
      >
        <span className="dot" />
        {brand.name}
      </button>
      <Navigation />
    </header>
  );
}
