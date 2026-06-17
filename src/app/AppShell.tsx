import { ReactNode, useEffect } from "react";
import { Header } from "../components/layout/Header";
import { Preloader } from "../components/layout/Preloader";
import { CursorGlow } from "../components/layout/CursorGlow";
import { ScrollProgress } from "../components/layout/ScrollProgress";
import { initLenis } from "../motion/lenis";
import { ScrollTrigger } from "../motion/scrollTriggers";

export function AppShell({ children }: { children: ReactNode }) {
  useEffect(() => {
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduce) document.documentElement.classList.add("no-motion");

    const destroy = initLenis();
    const onLoad = () => ScrollTrigger.refresh();
    window.addEventListener("load", onLoad);
    const t = window.setTimeout(() => ScrollTrigger.refresh(), 1200);

    return () => {
      destroy();
      window.removeEventListener("load", onLoad);
      clearTimeout(t);
      ScrollTrigger.getAll().forEach((s) => s.kill());
    };
  }, []);

  return (
    <>
      <div className="scanlines" aria-hidden />
      <div className="vignette" aria-hidden />
      <div className="grain" aria-hidden />
      <CursorGlow />
      <ScrollProgress />
      <Preloader />
      <Header />
      {children}
    </>
  );
}
