import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { SplitText } from "gsap/SplitText";

gsap.registerPlugin(ScrollTrigger, SplitText);

/**
 * Lightweight split-text: wraps each word of an element in a masked line so it
 * can be revealed with a clip-style upward slide. Avoids the paid SplitText
 * plugin. Returns the created word spans.
 */
export function splitWords(el: HTMLElement): HTMLElement[] {
  if (el.dataset.split === "done") {
    return Array.from(el.querySelectorAll<HTMLElement>(".split-word"));
  }
  const text = el.textContent ?? "";
  el.textContent = "";
  const words = text.split(/(\s+)/);
  const spans: HTMLElement[] = [];

  words.forEach((word) => {
    if (word.trim() === "") {
      el.appendChild(document.createTextNode(word));
      return;
    }
    const mask = document.createElement("span");
    mask.className = "split-line";
    mask.style.display = "inline-block";
    mask.style.overflow = "hidden";
    mask.style.verticalAlign = "top";
    // extend the clip box below the baseline so descenders (g, y, p, ß) and
    // tight line-heights are never cut off, without affecting layout spacing.
    mask.style.paddingBottom = "0.18em";
    mask.style.marginBottom = "-0.18em";
    mask.style.paddingRight = "0.04em";
    mask.style.marginRight = "-0.04em";

    const inner = document.createElement("span");
    inner.className = "split-word";
    inner.style.display = "inline-block";
    inner.style.willChange = "transform";
    inner.textContent = word;

    mask.appendChild(inner);
    el.appendChild(mask);
    spans.push(inner);
  });

  el.dataset.split = "done";
  return spans;
}

/** Split a headline and reveal its words on scroll with a masked slide. */
export function revealHeadline(
  el: HTMLElement,
  opts: { start?: string; stagger?: number; trigger?: Element } = {}
): gsap.core.Tween {
  const { start = "top 82%", stagger = 0.08, trigger = el } = opts;
  // GSAP SplitText (free in 3.13+) for masked line reveals; manual fallback.
  try {
    const split = new SplitText(el, { type: "lines", linesClass: "split-line", mask: "lines" });
    gsap.set(split.lines, { yPercent: 110 });
    return gsap.to(split.lines, {
      yPercent: 0,
      duration: 1.15,
      ease: "expo.out",
      stagger: Math.max(stagger, 0.1),
      scrollTrigger: { trigger, start },
    });
  } catch {
    const words = splitWords(el);
    gsap.set(words, { yPercent: 110 });
    return gsap.to(words, {
      yPercent: 0,
      duration: 1.2,
      ease: "expo.out",
      stagger,
      scrollTrigger: { trigger, start },
    });
  }
}
