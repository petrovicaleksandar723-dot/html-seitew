import { asset } from "@/lib/asset";

/* Brand contact */
export const MAIL = "cleanlinesstudio@example.com";

/* Hero stats */
export const STATS = [
  { value: 120, suffix: "+", label: "Betriebe unterstützt" },
  { value: 4.9, suffix: "★", label: "Kundenzufriedenheit", decimals: 1 },
  { value: 30, suffix: "+", label: "Ideen pro Monat" },
] as const;

export const HERO_CHIPS = [
  "Keine Mindestlaufzeit",
  "Monatlich kündbar",
  "Antwort in 24 Std.",
];

/* Leistungen */
export const SERVICES = [
  {
    icon: "play",
    title: "Reel-Konzepte",
    body: "Starke Ideen mit Hook, Ablauf und CTA – damit deine Reels nicht einfach nur schön aussehen, sondern Aufmerksamkeit bringen.",
  },
  {
    icon: "pen",
    title: "Captions",
    body: "Texte, die nicht nach Vorlage klingen, sondern zu deinem Betrieb passen und deine Kunden direkt ansprechen.",
  },
  {
    icon: "globe",
    title: "Google-Beiträge",
    body: "Regelmäßige Beiträge für dein Google-Profil, damit dein Betrieb aktiver, sichtbarer und professioneller wirkt.",
  },
  {
    icon: "star",
    title: "Bewertungsantworten",
    body: "Freundliche, professionelle Antworten auf Kundenbewertungen – ohne dass du jedes Mal überlegen musst, was du schreiben sollst.",
  },
  {
    icon: "calendar",
    title: "Monatsplan",
    body: "Ein klarer Content-Plan für den ganzen Monat, damit du nicht jeden Tag neu überlegen musst, was online gehen soll.",
  },
] as const;

/* Showreel cards (phone mockups) */
export const SHOWREEL = [
  { src: asset("/videos/reel-1.mp4"), cap: "Reel-Produktion" },
  { src: asset("/videos/reel-2.mp4"), cap: "Hook & Schnitt" },
  { src: asset("/videos/reel-3.mp4"), cap: "Story-Reel" },
  { src: asset("/videos/reel-4.mp4"), cap: "Promo-Clip" },
  { src: asset("/videos/final.mp4"), cap: "Brand-Film" },
] as const;

export const HERO_VIDEO = asset("/videos/hero.mp4");

/* Branchen — external CDN stills already generated for this brand */
const CDN = "https://d8j0ntlcm91z4.cloudfront.net/user_3F5SAXdcmbfUfI7TTqv7gEJmXiN/";
export const BRANCHES = [
  {
    tab: "Friseure",
    img: CDN + "hf_20260614_121505_3df017d3-688d-4350-9362-5167c2efd165.png",
    reel: "Aus einem normalen Haarschnitt wird ein Vorher-Nachher-Moment",
    cap: "Neuer Look, neues Gefühl. Zeig deinen Kunden, was mit dem richtigen Schnitt möglich ist.",
    google: "Neue Termine frei – sichere dir jetzt deinen Wunschtermin für deinen neuen Look.",
    cta: "Jetzt Wunschtermin sichern",
    metric: "Mehr Sichtbarkeit",
  },
  {
    tab: "Restaurants",
    img: CDN + "hf_20260614_121507_0737227a-d299-4c94-bdf2-ff59219631c8.png",
    reel: "Ein Gericht vom ersten Handgriff bis zum fertigen Teller",
    cap: "Appetit entsteht nicht durch Zufall. Zeig, was bei dir frisch, ehrlich und besonders ist.",
    google: "Heute frisch für dich gekocht – reservier dir deinen Tisch fürs Wochenende.",
    cta: "Jetzt Tisch reservieren",
    metric: "Mehr Gäste",
  },
  {
    tab: "Handwerker",
    img: CDN + "hf_20260614_121508_62c6e4c1-ec60-419e-b7c9-4a3daf92dc62.png",
    reel: "Aus Problem wird Lösung – eine Baustelle in 20 Sekunden",
    cap: "Kunden kaufen Vertrauen. Zeig sauber, wie du arbeitest und warum man dich beauftragen sollte.",
    google: "Saubere Arbeit, faire Preise – fordere jetzt dein unverbindliches Angebot an.",
    cta: "Jetzt Angebot anfordern",
    metric: "Mehr Vertrauen",
  },
  {
    tab: "Kosmetikstudios",
    img: CDN + "hf_20260614_121510_e1bfc022-7446-419f-adca-0812f520f80f.png",
    reel: "Behandlung, Atmosphäre und Ergebnis in einem ruhigen Premium-Clip",
    cap: "Deine Kunden buchen nicht nur eine Behandlung. Sie buchen ein Gefühl von Pflege, Ruhe und Qualität.",
    google: "Gönn dir eine Auszeit – buche jetzt deine Wohlfühl-Behandlung bei uns.",
    cta: "Jetzt Behandlung buchen",
    metric: "Mehr Wohlgefühl",
  },
  {
    tab: "Fahrschulen",
    img: CDN + "hf_20260615_003121_1f780c2f-d658-48e5-829c-32dcce3f1e8c.png",
    reel: "3 Dinge, die jeder Fahrschüler vor der Prüfung wissen sollte",
    cap: "Nimm deinen Schülern die Angst und zeig, dass deine Fahrschule verständlich, modern und nahbar ist.",
    google: "Neuer Kurs startet bald – melde dich jetzt an und starte sicher durch.",
    cta: "Jetzt zum Kurs anmelden",
    metric: "Mehr Anmeldungen",
  },
  {
    tab: "Fitnessstudios",
    img: CDN + "hf_20260615_003122_2462d848-1d79-4383-807c-62e8689a9a0c.png",
    reel: "Ein einfaches Workout, das jeder sofort ausprobieren kann",
    cap: "Keine Ausreden. Keine komplizierten Pläne. Nur ein klarer Start in ein stärkeres Ich.",
    google: "Probetraining gratis – komm vorbei und finde deinen Einstieg, der wirklich passt.",
    cta: "Jetzt Probetraining sichern",
    metric: "Mehr Motivation",
  },
] as const;

/* Editorial pills */
export const PILLS = [
  { icon: "bulb", label: "Fertige Ideen" },
  { icon: "pen", label: "Fertige Texte" },
  { icon: "calendar", label: "Klarer Monatsplan" },
] as const;

/* Before / After */
export const BEFORE = [
  "Jeden Tag überlegen, was man posten könnte",
  "Mal aktiv, dann wieder wochenlang nichts",
  "Keine klare Linie im Auftritt",
  "Texte fühlen sich gezwungen an",
  "Wenig Sichtbarkeit, kaum neue Anfragen",
  "Social Media bleibt immer liegen",
];
export const AFTER = [
  "Ein fertiger Monatsplan im Voraus",
  "Regelmäßiger Content ohne Stress",
  "Texte, die professionell & natürlich klingen",
  "Mehr Vertrauen bei neuen Kunden",
  "Einheitlicher Auftritt auf Instagram & Google",
  "Du sparst Zeit und wirkst aktiver",
];

/* Pricing */
export const PLANS = [
  {
    icon: "spark",
    name: "Starter",
    price: "250€",
    cadence: "/Monat",
    desc: "Der einfache Einstieg für Betriebe, die endlich regelmäßig sichtbar sein wollen.",
    features: [
      "8 Reel-Konzepte pro Monat",
      "12 fertige Captions",
      "4 Google-Beiträge",
      "1 klarer Monatsplan",
    ],
    cta: "Starter anfragen",
    featured: false,
  },
  {
    icon: "growth",
    name: "Wachstum",
    price: "490€",
    cadence: "/Monat",
    desc: "Für Betriebe, die mehr posten, professioneller wirken und mehr Anfragen bekommen wollen.",
    features: [
      "16 Reel-Konzepte pro Monat",
      "30 fertige Captions",
      "8 Google-Beiträge",
      "Bewertungsantworten",
      "Monatsplan + Strategie-Call",
    ],
    cta: "Wachstum anfragen",
    featured: true,
  },
  {
    icon: "crown",
    name: "Premium",
    price: "890€",
    cadence: "/Monat",
    desc: "Für Betriebe, die ihren Content komplett auslagern und dauerhaft präsent sein wollen.",
    features: [
      "Unbegrenzte Reel-Konzepte",
      "60+ Captions pro Monat",
      "Tägliche Google-Beiträge",
      "Persönlicher Ansprechpartner",
      "Priorisierter Support",
    ],
    cta: "Premium anfragen",
    featured: false,
  },
] as const;

export const PAYS = ["VISA", "Mastercard", "PayPal", "Klarna", "SEPA", "Apple Pay"];

/* Einzelaufträge */
export const EINZEL = [
  {
    icon: "browser",
    title: "Website-Design",
    tag: "ab 1.490€",
    body: "Eine moderne Website, die auf dem Handy stark aussieht, Vertrauen schafft und Kunden zur Anfrage bringt.",
  },
  {
    icon: "spark",
    title: "Logo & Branding",
    tag: "ab 590€",
    body: "Ein sauberer Markenauftritt mit Logo, Farben und Schriften, damit dein Betrieb hochwertiger wirkt.",
  },
  {
    icon: "play",
    title: "Reel-Produktion",
    tag: "ab 290€ / Reel",
    body: "Fertig geschnittene Reels mit Hook, Untertiteln, Musik und klarer Botschaft – bereit zum Veröffentlichen.",
  },
  {
    icon: "share",
    title: "Social-Media-Setup",
    tag: "ab 390€",
    body: "Wir optimieren dein Profil, deine Bio, Highlights und deinen ersten Content-Aufbau für einen starken Start.",
  },
] as const;

/* Reviews */
export const REVIEWS = [
  {
    text: "Ich musste vorher jeden Post selbst überlegen. Jetzt bekomme ich jeden Monat einen klaren Plan und kann einfach arbeiten.",
    name: "Sarah M.",
    role: "Friseursalon",
  },
  {
    text: "Unsere Seite wirkt viel aktiver und professioneller. Man merkt sofort, dass endlich eine Linie drin ist.",
    name: "Marco L.",
    role: "Restaurant",
  },
  {
    text: "Die Texte klingen nicht künstlich, sondern wirklich nach unserem Betrieb. Genau das war mir wichtig.",
    name: "Daniel K.",
    role: "Handwerksbetrieb",
  },
  {
    text: "Endlich jemand, der versteht, dass lokale Betriebe keine Zeit für ständiges Content-Grübeln haben.",
    name: "Lena R.",
    role: "Kosmetikstudio",
  },
] as const;

/* FAQ */
export const FAQ = [
  {
    q: "Wie schnell bekomme ich meinen ersten Content?",
    a: "Nach dem Start bekommst du innerhalb von 5 Werktagen deinen ersten fertigen Monatsplan mit Ideen, Texten und Beiträgen.",
  },
  {
    q: "Muss ich lange Vertragslaufzeiten eingehen?",
    a: "Nein. Alle Pakete sind monatlich kündbar. Du bleibst flexibel und kannst jederzeit entscheiden, wie es weitergeht.",
  },
  {
    q: "Funktioniert das auch für meine Branche?",
    a: "Ja. Wir passen die Inhalte an deinen Betrieb an – egal ob Friseur, Restaurant, Handwerk, Kosmetik, Fahrschule, Fitnessstudio oder ein anderer lokaler Service.",
  },
  {
    q: "Macht ihr auch fertige Videos?",
    a: "Ja. Die Konzepte und Skripte sind in den Paketen enthalten. Fertig produzierte Reels kannst du zusätzlich als Einzelauftrag buchen.",
  },
  {
    q: "Was brauche ich zum Start?",
    a: "Nur ein paar Infos zu deinem Betrieb, deiner Zielgruppe und deinem Angebot. Danach bauen wir daraus deinen Content-Plan.",
  },
] as const;
