/** Split an element's text into masked word spans (keeps inline tags intact). */
export function splitWords(el: HTMLElement): HTMLElement[] {
  if (el.dataset.split === "done") {
    return Array.from(el.querySelectorAll<HTMLElement>(".word > span"));
  }
  const html = el.innerHTML;
  const tokens = html.match(/<[a-zA-Z][^>]*>[\s\S]*?<\/[a-zA-Z]+>|[^\s]+|\s+/g) || [
    el.textContent || "",
  ];
  el.innerHTML = tokens
    .map((t) =>
      /^\s+$/.test(t) ? " " : `<span class="word"><span>${t}</span></span>`
    )
    .join("");
  el.dataset.split = "done";
  return Array.from(el.querySelectorAll<HTMLElement>(".word > span"));
}
