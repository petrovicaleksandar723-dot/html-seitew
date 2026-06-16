import { useEffect, useRef, useState } from "react";
import {
  Film, Calendar, Sparkles, Globe, Star, Building2, Layers, MessageCircle, Eye, LucideIcon,
} from "lucide-react";
import { OS, CONTROL, INDUSTRIES, PACKAGES, whatsappHref, OSApp } from "../../content/siteContent";
import { KineticLabel } from "../ui/KineticLabel";
import { SplitHeadline } from "../ui/SplitHeadline";
import { SectionNumber } from "../ui/SectionNumber";
import { IpadFrame } from "../ui/IpadFrame";
import { OSModule } from "../ui/OSModule";
import { useScrollReveal } from "../../motion/useScrollReveal";
import { buildControlCenter } from "../../motion/controlCenterTimeline";
import { gsap } from "../../motion/scrollTriggers";
import { scrollToId } from "../../motion/lenis";

const ICONS: Record<string, LucideIcon> = {
  reels: Film, kalender: Calendar, kivisuals: Sparkles, google: Globe, reviews: Star,
  branchen: Building2, pakete: Layers, whatsapp: MessageCircle, preview: Eye,
};

function Preview({ app }: { app: OSApp }) {
  switch (app.preview) {
    case "video":
      return (
        <div className="osp-video">
          <video key={app.video} src={app.video} autoPlay muted loop playsInline preload="metadata" />
          <div className="osp-video-veil" />
          <span className="osp-badge"><i /> LIVE</span>
        </div>
      );
    case "calendar":
      return (
        <div className="osp-cal">
          {Array.from({ length: 28 }).map((_, i) => (
            <span key={i} className={[2, 5, 9, 12, 16, 19, 23, 26].includes(i) ? "on" : ""} />
          ))}
        </div>
      );
    case "posts":
      return (
        <div className="osp-post">
          <div className="osp-post-h">
            <span className="osp-ava" />
            <div>
              <b>Dein Betrieb</b>
              <small>Google · gerade eben</small>
            </div>
          </div>
          <p>Diese Woche kurzfristig freie Termine — sichere dir deinen Platz.</p>
          <span className="osp-cta">Termin sichern</span>
        </div>
      );
    case "reviews":
      return (
        <div className="osp-rev">
          <div className="osp-stars">★★★★★</div>
          <p>„Schnell, professionell und genau unser Stil. Sieht endlich aus wie eine echte Marke."</p>
          <span className="osp-rev-by">Antwort fertig in Sekunden</span>
        </div>
      );
    case "industries":
      return (
        <div className="osp-ind">
          {INDUSTRIES.slice(0, 6).map((i) => (
            <span key={i.id}>{i.name}</span>
          ))}
        </div>
      );
    case "packages":
      return (
        <div className="osp-pak">
          {PACKAGES.map((p) => (
            <div key={p.id} className={p.featured ? "feat" : ""}>
              <b>{p.name}</b>
              <span>{p.price}</span>
            </div>
          ))}
        </div>
      );
    case "whatsapp":
      return (
        <div className="osp-wa">
          <div className="osp-wa-bubble">Hey! Ich hätte gern eine Content-Preview für meinen Betrieb 👋</div>
          <a
            className="osp-cta wa"
            href={whatsappHref("Hallo CleanLines Studio, ich möchte eine kostenlose Content-Preview anfragen.")}
            target="_blank"
            rel="noopener noreferrer"
          >
            WhatsApp öffnen
          </a>
        </div>
      );
    case "preview":
    default:
      return (
        <div className="osp-prev">
          <div className="osp-prev-glow" />
          <b>Kostenlose Content-Preview</b>
          <p>In 24 Stunden siehst du, wie dein Content aussehen könnte.</p>
          <a
            className="osp-cta"
            href="#final"
            onClick={(e) => {
              e.preventDefault();
              scrollToId("final");
            }}
          >
            Preview anfragen
          </a>
        </div>
      );
  }
}

export function ControlCenterSection() {
  const ref = useRef<HTMLElement>(null);
  const ipadRef = useRef<HTMLDivElement>(null);
  useScrollReveal(ref);
  const [active, setActive] = useState<OSApp>(CONTROL.apps[0]);

  useEffect(() => {
    const section = ref.current;
    const ipad = ipadRef.current;
    if (!section || !ipad) return;
    const apps = Array.from(section.querySelectorAll<HTMLElement>(".os-app"));
    const mm = gsap.matchMedia();
    mm.add("(min-width:1024px)", () => buildControlCenter({ section, ipad, apps }));
    return () => mm.revert();
  }, []);

  return (
    <section id="system" className="scene" ref={ref}>
      <div className="wrap cc-grid">
        <div className="cc-copy">
          <SectionNumber n="02" />
          <KineticLabel>{OS.label}</KineticLabel>
          <SplitHeadline text={OS.headline} gold={OS.gold} />
          <p className="lede" data-fade>
            {OS.lede}
          </p>
          <p className="cc-note" data-fade>
            <span /> {OS.note} →
          </p>
        </div>

        <div className="cc-stage">
          <IpadFrame innerRef={ipadRef}>
            <div className="os-bar">
              <span className="os-brand">CleanLines OS</span>
              <span className="os-dots">
                <i /><i /><i />
              </span>
              <span className="os-time">9:41</span>
            </div>
            <div className="os-body">
              <div className="os-apps">
                {CONTROL.apps.map((a) => (
                  <OSModule
                    key={a.id}
                    label={a.label}
                    icon={ICONS[a.id]}
                    active={active.id === a.id}
                    onActivate={() => setActive(a)}
                  />
                ))}
              </div>
              <div className="os-preview">
                <Preview app={active} />
                <div className="os-cap">
                  <span className="os-cap-dot" /> {active.caption}
                </div>
              </div>
            </div>
          </IpadFrame>
        </div>
      </div>
    </section>
  );
}
