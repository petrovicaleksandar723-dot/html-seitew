import { brand, mailto, hero } from "../../content/siteContent";
import { scrollToTarget } from "../../motion/lenis";
import Navigation from "./Navigation";

/** Fixed header with brand mark, section navigation and a persistent CTA. */
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

      <div className="header__right">
        <Navigation />
        <a
          className="header__cta"
          href={mailto("Kostenlose Content-Preview")}
          data-cursor="hover"
        >
          {hero.ctaPrimary}
        </a>
      </div>
    </header>
  );
}
