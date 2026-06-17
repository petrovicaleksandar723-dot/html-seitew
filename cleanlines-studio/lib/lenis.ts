import type Lenis from "lenis";

/** Shared Lenis instance so the page-transition curtain can drive scrolling. */
export const lenisRef: { current: Lenis | null } = { current: null };
