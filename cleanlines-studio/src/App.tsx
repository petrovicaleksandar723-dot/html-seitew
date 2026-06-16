import { useEffect } from "react";
import { useLenis } from "./motion/useLenis";
import { Cursor } from "./components/Cursor";
import { Nav } from "./components/Nav";
import { Marquee } from "./components/Marquee";
import { Button } from "./components/Button";
import { ReelProvider } from "./components/ReelViewer";
import { Hero } from "./sections/Hero";
import { Problem } from "./sections/Problem";
import { Solution } from "./sections/Solution";
import { Showcase } from "./sections/Showcase";
import { Industries } from "./sections/Industries";
import { Transform } from "./sections/Transform";
import { Process } from "./sections/Process";
import { Packages } from "./sections/Packages";
import { Proof } from "./sections/Proof";
import { Faq } from "./sections/Faq";
import { Cta } from "./sections/Cta";
import { MAIL } from "./data/content";

export default function App() {
  useLenis();

  useEffect(() => {
    const header = document.getElementById("header");
    const progress = document.getElementById("progress");
    const dock = document.getElementById("dock");
    const links = Array.from(document.querySelectorAll<HTMLAnchorElement>(".nav a[data-spy]"));
    const secs = links.map((a) => document.getElementById(a.dataset.spy || ""));
    let lastY = 0;
    let queued = false;
    let spy = -1;

    const frame = () => {
      queued = false;
      const y = window.scrollY || 0;
      const vh = window.innerHeight;
      const max = document.documentElement.scrollHeight - vh || 1;
      const r = Math.min(1, Math.max(0, y / max));
      if (progress) progress.style.transform = `scaleX(${r.toFixed(4)})`;
      if (header) {
        header.classList.toggle("solid", y > 40);
        header.classList.toggle("hide", y > lastY && y > vh * 0.9 && !document.body.classList.contains("menu"));
      }
      if (dock) dock.classList.toggle("show", y > vh * 1.05 && r < 0.92);
      const probe = y + vh * 0.34;
      let a = -1;
      secs.forEach((s, i) => {
        if (s && s.offsetTop <= probe) a = i;
      });
      if (a !== spy) {
        spy = a;
        links.forEach((l, i) => l.classList.toggle("active", i === a));
      }
      lastY = y;
    };
    const onScroll = () => {
      if (!queued) {
        queued = true;
        requestAnimationFrame(frame);
      }
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll, { passive: true });
    frame();
    return () => {
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", onScroll);
    };
  }, []);

  return (
    <ReelProvider>
      <div className="bg-base" />
      <div className="bg-aura" aria-hidden="true" />
      <div className="bg-grid" aria-hidden="true" />
      <Cursor />
      <div className="progress" id="progress" aria-hidden="true" />
      <Nav />
      <main>
        <Hero />
        <Marquee />
        <Problem />
        <Solution />
        <Showcase />
        <Industries />
        <Transform />
        <Process />
        <Packages />
        <Proof />
        <Faq />
        <Cta />
      </main>
      <div className="dock" id="dock">
        <span className="t">Kostenlose Content-Preview</span>
        <Button href={MAIL}>Anfragen</Button>
      </div>
    </ReelProvider>
  );
}
