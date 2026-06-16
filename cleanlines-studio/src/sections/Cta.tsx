import { Reveal } from "../motion/Reveal";
import { Button } from "../components/Button";
import { Logo } from "../components/Logo";
import { MAIL, WHATSAPP } from "../data/content";

export function Cta() {
  return (
    <>
      <section className="section final" id="kontakt">
        <div className="wrap">
          <Reveal>
            <span className="eyebrow">Jetzt starten</span>
            <h2 className="h2">
              Bereit, online endlich <span className="shine">premium</span> zu wirken?
            </h2>
            <p className="sub" style={{ margin: "16px auto 0" }}>
              Schick uns kurz deinen Betrieb – mit einer kostenlosen Content-Preview zeigen wir dir, was möglich ist. Unverbindlich, persönlich, ohne Zahlung.
            </p>
            <div className="btns center" style={{ marginTop: 28 }}>
              <Button href={MAIL}>Kostenlose Content-Preview</Button>
              <Button href={WHATSAPP} variant="wa" external>
                WhatsApp-Anfrage
              </Button>
            </div>
          </Reveal>
        </div>
      </section>
      <footer>
        <div className="wrap">
          <a className="brand" href="#top">
            <Logo />
            Cleanlines <span>Studio</span>
          </a>
          <p style={{ marginTop: 4 }}>Cinematisches Content-Studio für lokale Betriebe</p>
          <p style={{ marginTop: 6 }}>
            <a href="mailto:cleanlinesstudio@example.com" style={{ color: "var(--gold-2)" }}>
              cleanlinesstudio@example.com
            </a>
          </p>
          <div className="fl">
            <a href="#kontakt">Impressum</a>
            <a href="#kontakt">Datenschutz</a>
            <a href="#kontakt">Kontakt</a>
          </div>
        </div>
      </footer>
    </>
  );
}
