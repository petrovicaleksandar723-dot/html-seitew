import { useCallback, useEffect, useState } from "react";
import Preloader from "../components/layout/Preloader";
import Header from "../components/layout/Header";
import CursorGlow from "../components/layout/CursorGlow";
import ScrollProgress from "../components/layout/ScrollProgress";
import HomePage from "./HomePage";
import { initLenis, destroyLenis, stopLenis, startLenis } from "../motion/lenis";
import { ScrollTrigger } from "../motion/scrollTriggers";

/**
 * Top-level shell: boots Lenis + GSAP, gates the experience behind the
 * preloader, and mounts the persistent UI layers (header, cursor, progress).
 */
export default function AppShell() {
  const [ready, setReady] = useState(false);

  useEffect(() => {
    initLenis();
    stopLenis(); // hold scroll during the preloader
    window.scrollTo(0, 0);
    return () => destroyLenis();
  }, []);

  const handleLoaded = useCallback(() => {
    setReady(true);
    startLenis();
    // recalc all triggers once layout + fonts have settled
    requestAnimationFrame(() => ScrollTrigger.refresh());
  }, []);

  // keep triggers honest after fonts/images load
  useEffect(() => {
    if (!ready) return;
    const onLoad = () => ScrollTrigger.refresh();
    window.addEventListener("load", onLoad);
    const t = setTimeout(() => ScrollTrigger.refresh(), 800);
    return () => {
      window.removeEventListener("load", onLoad);
      clearTimeout(t);
    };
  }, [ready]);

  return (
    <>
      <Preloader onComplete={handleLoaded} />
      <CursorGlow />
      <ScrollProgress />
      <Header />
      <HomePage ready={ready} />
      <div className="grain" aria-hidden />
      <div className="vignette" aria-hidden />
    </>
  );
}
