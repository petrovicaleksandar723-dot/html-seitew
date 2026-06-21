"use client";

import { Reveal } from "@/components/cl/ui";
import { Icon } from "@/components/cl/icons";
import { MAIL } from "@/lib/cl-data";

export function ClFooter() {
  return (
    <footer className="border-t border-line px-5 py-12 text-center text-[13px] text-dim">
      <Reveal>
        <div className="mx-auto w-full max-w-[600px]">
          <div className="mb-3.5 inline-flex items-center justify-center gap-2">
            <Icon name="mark" className="h-[26px] w-[26px] text-gold" />
            <span className="font-display">
              <b className="font-bold text-ink">CleanLines</b> Studio
            </span>
          </div>

          <p>Creative Content Hub für lokale Betriebe</p>

          <a
            href={`mailto:${MAIL}`}
            className="mt-3 inline-block text-gold-bright"
          >
            {MAIL}
          </a>
        </div>
      </Reveal>
    </footer>
  );
}
