import { useEffect, useRef, useState, FormEvent } from "react";
import { MessageCircle } from "lucide-react";
import { FINAL, mailtoHref, whatsappHref } from "../../content/siteContent";
import { KineticLabel } from "../ui/KineticLabel";
import { SplitHeadline } from "../ui/SplitHeadline";
import { MagneticButton } from "../ui/MagneticButton";
import { useScrollReveal } from "../../motion/useScrollReveal";

const BRANCHEN = [
  "Restaurant / Gastro",
  "Friseur / Barber",
  "Gym / Fitness",
  "Café",
  "Autohaus / Detailing",
  "Kosmetikstudio",
  "Klinik / Praxis",
  "Immobilien",
  "Handwerk",
  "Andere Branche",
];

export function FinalCTASection() {
  const ref = useRef<HTMLElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  useScrollReveal(ref);

  const [form, setForm] = useState({ betrieb: "", branche: BRANCHEN[0], email: "", nachricht: "" });

  useEffect(() => {
    const v = videoRef.current;
    const sec = ref.current;
    if (!v || !sec) return;
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((x) => {
          if (x.isIntersecting) {
            if (!v.src) v.src = "/assets/videos/final.mp4";
            v.play().catch(() => {});
          } else {
            v.pause();
          }
        });
      },
      { threshold: 0.15 }
    );
    io.observe(sec);
    return () => io.disconnect();
  }, []);

  const buildMessage = () =>
    [
      "Hallo CleanLines Studio,",
      "",
      "ich möchte gerne meine kostenlose Content-Preview erhalten.",
      "",
      `Betrieb: ${form.betrieb}`,
      `Branche: ${form.branche}`,
      `E-Mail: ${form.email}`,
      ...(form.nachricht ? ["", `Nachricht: ${form.nachricht}`] : []),
      "",
      "Viele Grüße",
    ].join("\n");

  const onSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!form.betrieb.trim() || !form.email.trim()) return;
    window.location.href = mailtoHref(`Kostenlose Content-Preview für ${form.betrieb.trim()}`, buildMessage());
  };

  const set = (k: keyof typeof form) => (e: { target: { value: string } }) =>
    setForm((f) => ({ ...f, [k]: e.target.value }));

  return (
    <section id="final" className="scene" ref={ref}>
      <div className="final-bg" aria-hidden>
        <video ref={videoRef} muted loop playsInline preload="none" />
      </div>
      <div className="wrap">
        <div className="final-grid">
          <div className="final-copy">
            <KineticLabel>{FINAL.label}</KineticLabel>
            <SplitHeadline text={`${FINAL.headline[0]} ${FINAL.headline[1]}`} gold={FINAL.gold} />
            <p className="lede" data-fade>
              {FINAL.sub}
            </p>
            <div className="final-actions" data-fade>
              <MagneticButton
                variant="primary"
                href={mailtoHref(
                  "Kostenlose Content-Preview",
                  "Hallo CleanLines Studio,\n\nich möchte eine kostenlose Content-Preview anfragen.\n\nBetrieb:\nBranche:\n\nViele Grüße"
                )}
              >
                {FINAL.primary}
              </MagneticButton>
              <MagneticButton
                variant="wa"
                href={whatsappHref("Hallo CleanLines Studio, ich möchte eine kostenlose Content-Preview anfragen.")}
                target="_blank"
                rel="noopener"
              >
                <MessageCircle size={17} /> {FINAL.whatsapp}
              </MagneticButton>
            </div>
          </div>

          <div className="cta-form reveal">
            <form onSubmit={onSubmit}>
              <div className="fg">
                <label htmlFor="f-betrieb">Name deines Betriebs *</label>
                <input id="f-betrieb" value={form.betrieb} onChange={set("betrieb")} placeholder="z. B. Barber Elite oder Auto Glanz" required />
              </div>
              <div className="fg">
                <label htmlFor="f-branche">Branche *</label>
                <select id="f-branche" value={form.branche} onChange={set("branche")}>
                  {BRANCHEN.map((b) => (
                    <option key={b}>{b}</option>
                  ))}
                </select>
              </div>
              <div className="fg">
                <label htmlFor="f-email">Deine E-Mail-Adresse *</label>
                <input id="f-email" type="email" value={form.email} onChange={set("email")} placeholder="name@betrieb.de" required />
              </div>
              <div className="fg">
                <label htmlFor="f-msg">Nachricht (optional)</label>
                <textarea id="f-msg" value={form.nachricht} onChange={set("nachricht")} placeholder="z. B. gewünschtes Paket, Standort, aktuelle Situation…" />
              </div>
              <div className="form-actions">
                <button type="submit" className="btn btn-primary">
                  Per E-Mail anfragen
                </button>
                <button type="button" className="btn btn-wa" onClick={() => window.open(whatsappHref(buildMessage()), "_blank", "noopener")}>
                  <MessageCircle size={17} /> Per WhatsApp anfragen
                </button>
              </div>
              <p className="form-hint">Unverbindlich &amp; kostenlos. Deine Daten werden nur zur Beantwortung deiner Anfrage verwendet.</p>
            </form>
          </div>
        </div>
      </div>
    </section>
  );
}
