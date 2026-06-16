import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

export const EASE = {
  out: "expo.out",
  power: "power3.out",
  circ: "circ.out",
};

export { gsap, ScrollTrigger };
