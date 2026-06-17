import { NAV_LINKS } from "@/lib/constants";
import { LogoMark } from "@/components/ui/logo";

export function Footer() {
  return (
    <footer className="border-t border-line py-14">
      <div className="shell content flex flex-col gap-10">
        <div className="flex flex-col items-start justify-between gap-8 md:flex-row md:items-center">
          <div className="flex items-center gap-3">
            <LogoMark className="h-10 w-10 drop-shadow-[0_2px_12px_rgba(216,178,116,0.45)]" />
            <div>
              <div className="font-display text-[16px] font-extrabold tracking-[0.1em]">
                CLEANLINES STUDIOS
              </div>
              <div className="font-body text-[12.5px] text-muted">
                Premium Content für lokale Betriebe
              </div>
            </div>
          </div>

          <nav className="flex flex-wrap gap-x-6 gap-y-2">
            {NAV_LINKS.map((l) => (
              <a
                key={l.href}
                href={l.href}
                className="font-body text-[13px] text-dim transition-colors hover:text-ink"
              >
                {l.label}
              </a>
            ))}
          </nav>
        </div>

        <div className="flex flex-col items-start justify-between gap-3 border-t border-line pt-8 font-body text-[12.5px] text-muted md:flex-row md:items-center">
          <span>© {new Date().getFullYear()} Cleanlines Studio. Alle Rechte vorbehalten.</span>
          <div className="flex gap-6">
            <a href="#" className="transition-colors hover:text-ink">
              Impressum
            </a>
            <a href="#" className="transition-colors hover:text-ink">
              Datenschutz
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
