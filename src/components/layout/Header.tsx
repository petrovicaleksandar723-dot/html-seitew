import { useEffect, useRef, useState } from "react";
import { Navigation } from "./Navigation";
import { MagneticButton } from "../ui/MagneticButton";
import { scrollToId } from "../../motion/lenis";

export function Header() {
  const ref = useRef<HTMLElement>(null);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    let lastY = window.scrollY || 0;
    const on = () => {
      const y = window.scrollY || 0;
      const el = ref.current;
      if (!el) return;
      el.classList.toggle("shrink", y > 40);
      if (y > lastY && y > 220 && !open) el.classList.add("hide");
      else el.classList.remove("hide");
      lastY = y;
    };
    window.addEventListener("scroll", on, { passive: true });
    return () => window.removeEventListener("scroll", on);
  }, [open]);

  useEffect(() => {
    document.body.style.overflow = open ? "hidden" : "";
  }, [open]);

  return (
    <>
      <header ref={ref} className="site-header">
        <div className="wrap header-inner">
          <a
            href="#hero"
            className="logo"
            onClick={(e) => {
              e.preventDefault();
              scrollToId("hero");
            }}
          >
            <span className="mk">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none">
                <path d="M4 4v16h7" stroke="#160f04" strokeWidth="2.6" strokeLinecap="round" />
                <path d="M14 4v9h6" stroke="#160f04" strokeWidth="2.6" strokeLinecap="round" />
              </svg>
            </span>
            <span>
              CleanLines<span className="gold-text">.</span>
            </span>
          </a>

          <nav className="nav-desk" aria-label="Hauptnavigation">
            <Navigation />
          </nav>

          <MagneticButton to="final" variant="primary" className="header-cta desk">
            Content-Preview sichern
          </MagneticButton>

          <button
            className={`burger ${open ? "open" : ""}`}
            aria-label="Menü"
            aria-expanded={open}
            onClick={() => setOpen((o) => !o)}
          >
            <span />
            <span />
            <span />
          </button>
        </div>
      </header>

      <div className={`mobile-nav ${open ? "open" : ""}`}>
        <Navigation onNavigate={() => setOpen(false)} />
        <MagneticButton to="final" variant="primary" onClick={() => setOpen(false)}>
          Content-Preview sichern
        </MagneticButton>
      </div>
    </>
  );
}
