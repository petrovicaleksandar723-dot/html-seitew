import { useState } from "react";
import { Logo } from "./Logo";
import { NAV, MAIL } from "../data/content";

export function Nav() {
  const [open, setOpen] = useState(false);
  const toggle = (v: boolean) => {
    setOpen(v);
    document.body.classList.toggle("menu", v);
  };
  return (
    <>
      <header className="header" id="header">
        <a className="brand" href="#top">
          <Logo />
          Cleanlines <span>Studio</span>
        </a>
        <nav className="nav" id="nav">
          {NAV.map((n) => (
            <a key={n.id} href={"#" + n.id} data-spy={n.id}>
              {n.label}
            </a>
          ))}
        </nav>
        <a className="head-cta" href={MAIL}>
          Content-Preview
        </a>
        <button className="burger" aria-label="Menü öffnen" onClick={() => toggle(!open)}>
          <i />
        </button>
      </header>
      <div className="mnav" id="mnav">
        {NAV.map((n) => (
          <a key={n.id} href={"#" + n.id} onClick={() => toggle(false)}>
            {n.label}
          </a>
        ))}
        <a className="btn btn-primary" href={MAIL} onClick={() => toggle(false)}>
          Kostenlose Content-Preview
        </a>
      </div>
    </>
  );
}
