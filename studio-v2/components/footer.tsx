export function Footer() {
  return (
    <footer className="border-t border-line py-12">
      <div
        className="shell flex flex-col items-center justify-between gap-6 sm:flex-row"
        style={{ ["--max" as string]: "1280px" }}
      >
        <div className="flex items-center gap-2.5">
          <span className="grid h-7 w-7 place-items-center rounded-[7px] bg-gradient-to-br from-gold-bright to-gold-deep text-[13px] font-extrabold text-[#1a1206]">
            C
          </span>
          <span className="font-display text-[14px] font-bold tracking-tight">
            Clean Lines <span className="text-muted">Studios</span>
          </span>
        </div>
        <p className="font-body text-[13px] text-muted">
          © {new Date().getFullYear()} Clean Lines Studios — Content, der wirkt.
        </p>
        <div className="flex items-center gap-6 font-body text-[13px] text-dim">
          <a href="#" className="transition-colors hover:text-ink">
            Instagram
          </a>
          <a href="#" className="transition-colors hover:text-ink">
            Impressum
          </a>
        </div>
      </div>
    </footer>
  );
}
