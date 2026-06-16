import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from "react";

const ReelCtx = createContext<(src: string) => void>(() => {});
export const useReel = () => useContext(ReelCtx);

export function ReelProvider({ children }: { children: ReactNode }) {
  const [src, setSrc] = useState<string | null>(null);

  const open = useCallback((s: string) => {
    setSrc(s);
    document.body.style.overflow = "hidden";
  }, []);
  const close = useCallback(() => {
    setSrc(null);
    document.body.style.overflow = "";
  }, []);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") close();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [close]);

  return (
    <ReelCtx.Provider value={open}>
      {children}
      <div
        className={"viewer" + (src ? " open" : "")}
        aria-hidden={!src}
        onClick={(e) => {
          if (e.target === e.currentTarget) close();
        }}
      >
        <button className="x" aria-label="Schließen" onClick={close}>
          ✕
        </button>
        {src && <video src={src} playsInline loop autoPlay controls />}
      </div>
    </ReelCtx.Provider>
  );
}
