/**
 * Cleanlines Studio — single source of truth.
 *
 * Business content (prices, industries, FAQ, packages, add-ons, contact logic)
 * is preserved 1:1 from the existing Cleanlines website. Weak marketing copy
 * has been rewritten into stronger premium German where noted.
 *
 * ┌─────────────────────────────────────────────────────────────────────┐
 * │  TODO BEFORE GOING LIVE — fill in the real contact details below.    │
 * │  The original site shipped with placeholders; they are kept here so  │
 * │  the build works, but they must be replaced.                         │
 * └─────────────────────────────────────────────────────────────────────┘
 */

export const contact = {
  email: "cleanlinesstudio@example.com", // TODO: echte E-Mail eintragen
  whatsappNumber: "49XXXXXXXXXX", // TODO: echte WhatsApp-Nummer (Format 49..., ohne +)
  location: "München / Remote",
};

const waBase = `https://wa.me/${contact.whatsappNumber}`;

/** Build a mailto link with a subject and optional body. */
export function mailto(subject: string, body?: string): string {
  const params = new URLSearchParams();
  params.set("subject", subject);
  if (body) params.set("body", body);
  return `mailto:${contact.email}?${params.toString()}`;
}

/** Build a WhatsApp deep link with a prefilled message. */
export function whatsapp(text: string): string {
  return `${waBase}?text=${encodeURIComponent(text)}`;
}

export const brand = {
  name: "Cleanlines Studio",
  short: "Cleanlines",
  tagline: "Content Engine für lokale Marken",
};

export const hero = {
  eyebrow: "Cinematic Content System · Lokale Betriebe",
  headline: "Dein Betrieb. Als wäre er eine große Marke.",
  subline:
    "Cinematic Reels, KI-Visuals und Content-Systeme für lokale Betriebe, die online endlich hochwertig wirken wollen.",
  ctaPrimary: "Content-Preview sichern",
  ctaSecondary: "Showcase ansehen",
  hud: {
    status: "CONTENT ENGINE ONLINE",
    pipeline: "REELS / AI VISUALS / SOCIAL PRESENCE",
    location: "MÜNCHEN / REMOTE / 24H PREVIEW",
  },
  trust: ["Unverbindlich", "Persönlicher Kontakt", "Monatlich kündbar"],
  stats: [
    { label: "Lokal", value: "Für lokale Betriebe gebaut" },
    { label: "Preview", value: "Persönliche Content-Preview" },
    { label: "Founder", value: "Angebot für die ersten Betriebe" },
  ],
};

export const diagnosis = {
  eyebrow: "Diagnose",
  headline: "Dein Betrieb ist gut. Aber online sieht man es nicht.",
  subline:
    "Die meisten lokalen Betriebe liefern erstklassige Arbeit — und verschenken sie an einen Auftritt, der nicht mithält. Wir scannen, was fehlt.",
  meters: [
    { label: "Sichtbarkeit", state: "niedrig", value: 24 },
    { label: "Vertrauen", state: "unklar", value: 41 },
    { label: "Content-System", state: "fehlt", value: 8 },
  ],
  readouts: [
    "Posting unregelmäßig",
    "Kein roter Faden",
    "Profil wirkt leer",
    "Keine Wiedererkennung",
  ],
};

export const contentOS = {
  eyebrow: "Content Operating System",
  headline: "Ein System statt einzelner Posts.",
  body: "Du bekommst kein einzelnes Video. Du bekommst ein System, das deinen Betrieb regelmäßig hochwertig sichtbar macht.",
  core: "Cleanlines OS",
  modules: [
    "Reels",
    "KI-Visuals",
    "Google-Beiträge",
    "Captions",
    "Monatsplan",
    "Bewertungsantworten",
    "Posting-System",
    "Content-Kalender",
  ],
};

export interface ReelItem {
  src: string;
  title: string;
  meta: string;
  index: string;
}

/** Reel Cinema — real videos from /public/assets/videos. */
export const reelCinema = {
  eyebrow: "Reel Cinema",
  headline: "So sieht dein Content aus.",
  subline:
    "Echte Beispiele aus unseren Reel-Produktionen — fertig für Instagram, TikTok und Co.",
  reels: [
    { src: "/assets/videos/hero.mp4", title: "Brand Opener", meta: "Cinematic Hook · 0:12", index: "01" },
    { src: "/assets/videos/reel-1.mp4", title: "Story Reel", meta: "Hook & Schnitt · 0:18", index: "02" },
    { src: "/assets/videos/show-1.mp4", title: "Reel-Produktion", meta: "Vertical · 0:15", index: "03" },
    { src: "/assets/videos/reel-2.mp4", title: "Promo Clip", meta: "Aktion · 0:14", index: "04" },
    { src: "/assets/videos/show-2.mp4", title: "Hook & Schnitt", meta: "Untertitel · 0:16", index: "05" },
    { src: "/assets/videos/reel-3.mp4", title: "Atmosphäre", meta: "Premium Mood · 0:20", index: "06" },
    { src: "/assets/videos/show-3.mp4", title: "Story-Reel", meta: "Narrativ · 0:17", index: "07" },
    { src: "/assets/videos/reel-4.mp4", title: "Brand-Film", meta: "Signature · 0:22", index: "08" },
    { src: "/assets/videos/show-4.mp4", title: "Signature Cut", meta: "Final Grade · 0:19", index: "09" },
  ] as ReelItem[],
};

export interface Industry {
  name: string;
  reel: string;
  caption: string;
  google: string;
  cta: string;
  metric: string;
  glow: string;
  /** Background video used on the visual stage. */
  video: string;
}

/** Industries — preserved per-industry copy from the source site, extended. */
export const industries = {
  eyebrow: "Branchen",
  headline: "Content, der zu deinem Betrieb passt.",
  subline:
    "Jede Branche braucht andere Ideen, andere Worte, andere Inhalte. Kein Standard-Template — sondern Content, der zu deinem Alltag, deinen Kunden und deinem Angebot passt.",
  claims: ["Mehr Vertrauen", "Mehr Sichtbarkeit", "Mehr Anfragen", "Premium-Auftritt"],
  items: [
    {
      name: "Friseure",
      reel: "Aus einem normalen Haarschnitt wird ein Vorher-Nachher-Moment.",
      caption: "Neuer Look, neues Gefühl. Zeig deinen Kunden, was mit dem richtigen Schnitt möglich ist.",
      google: "Neue Termine frei – sichere dir jetzt deinen Wunschtermin für deinen neuen Look.",
      cta: "Jetzt Wunschtermin sichern",
      metric: "Mehr Sichtbarkeit",
      glow: "rgba(201,162,90,.55)",
      video: "/assets/videos/reel-1.mp4",
    },
    {
      name: "Restaurants",
      reel: "Ein Gericht vom ersten Handgriff bis zum fertigen Teller.",
      caption: "Appetit entsteht nicht durch Zufall. Zeig, was bei dir frisch, ehrlich und besonders ist.",
      google: "Heute frisch für dich gekocht – reservier dir deinen Tisch fürs Wochenende.",
      cta: "Jetzt Tisch reservieren",
      metric: "Mehr Gäste",
      glow: "rgba(214,120,60,.5)",
      video: "/assets/videos/reel-2.mp4",
    },
    {
      name: "Handwerker",
      reel: "Aus Problem wird Lösung – eine Baustelle in 20 Sekunden.",
      caption: "Kunden kaufen Vertrauen. Zeig sauber, wie du arbeitest und warum man dich beauftragen sollte.",
      google: "Saubere Arbeit, faire Preise – fordere jetzt dein unverbindliches Angebot an.",
      cta: "Jetzt Angebot anfordern",
      metric: "Mehr Vertrauen",
      glow: "rgba(70,120,190,.5)",
      video: "/assets/videos/reel-3.mp4",
    },
    {
      name: "Kosmetikstudios",
      reel: "Behandlung, Atmosphäre und Ergebnis in einem ruhigen Premium-Clip.",
      caption: "Deine Kunden buchen nicht nur eine Behandlung. Sie buchen ein Gefühl von Pflege, Ruhe und Qualität.",
      google: "Gönn dir eine Auszeit – buche jetzt deine Wohlfühl-Behandlung bei uns.",
      cta: "Jetzt Behandlung buchen",
      metric: "Mehr Wohlgefühl",
      glow: "rgba(206,108,150,.5)",
      video: "/assets/videos/show-1.mp4",
    },
    {
      name: "Autohäuser",
      reel: "Vom Wunschauto bis zur Übergabe – Fahrzeuge und Service im Clip.",
      caption: "Zeig deine Fahrzeuge, deinen Service und dein Team – damit Kunden dir schon vor dem Besuch vertrauen.",
      google: "Neue Fahrzeuge und Aktionen verfügbar – vereinbare jetzt deinen Termin bei uns.",
      cta: "Jetzt Termin vereinbaren",
      metric: "Mehr Vertrauen",
      glow: "rgba(60,170,170,.5)",
      video: "/assets/videos/show-2.mp4",
    },
    {
      name: "Fitnessstudios",
      reel: "Ein einfaches Workout, das jeder sofort ausprobieren kann.",
      caption: "Keine Ausreden. Keine komplizierten Pläne. Nur ein klarer Start in ein stärkeres Ich.",
      google: "Probetraining gratis – komm vorbei und finde deinen Einstieg, der wirklich passt.",
      cta: "Jetzt Probetraining sichern",
      metric: "Mehr Motivation",
      glow: "rgba(90,180,110,.5)",
      video: "/assets/videos/show-3.mp4",
    },
    {
      name: "Cafés",
      reel: "Latte Art, Morgenlicht und der erste Schluck – in einem Loop.",
      caption: "Atmosphäre verkauft. Zeig den Ort, an dem deine Gäste gerne ihren Tag beginnen.",
      google: "Frisch geröstet, jeden Morgen – komm vorbei und sichere dir deinen Lieblingsplatz.",
      cta: "Jetzt vorbeikommen",
      metric: "Mehr Stammgäste",
      glow: "rgba(190,140,80,.5)",
      video: "/assets/videos/show-4.mp4",
    },
    {
      name: "Kliniken",
      reel: "Kompetenz, Ruhe und moderne Ausstattung in einem seriösen Clip.",
      caption: "Vertrauen entscheidet. Zeig dein Team und deine Expertise, bevor der Patient anruft.",
      google: "Neue Termine verfügbar – vereinbare jetzt dein Beratungsgespräch.",
      cta: "Jetzt Termin vereinbaren",
      metric: "Mehr Vertrauen",
      glow: "rgba(90,150,200,.5)",
      video: "/assets/videos/reel-4.mp4",
    },
    {
      name: "Immobilien",
      reel: "Vom Eingang bis zur Aussicht – ein Objekt cinematisch inszeniert.",
      caption: "Ein Objekt verkauft sich über Emotion. Zeig Räume so, dass Interessenten sich darin sehen.",
      google: "Neues Objekt verfügbar – sichere dir jetzt deinen Besichtigungstermin.",
      cta: "Jetzt Besichtigung anfragen",
      metric: "Mehr Anfragen",
      glow: "rgba(150,130,90,.5)",
      video: "/assets/videos/final.mp4",
    },
  ] as Industry[],
};

export const transformation = {
  eyebrow: "Vorher / Nachher",
  headline: "Aus einem leeren Profil wird eine Marke.",
  before: {
    label: "Vorher",
    items: [
      "Unregelmäßige Posts",
      "Keine Ideen, kein roter Faden",
      "Keine klare Linie im Auftritt",
      "Texte wirken gezwungen",
      "Wenig Sichtbarkeit, kaum Anfragen",
      "Social Media bleibt ständig liegen",
    ],
  },
  after: {
    label: "Nachher",
    items: [
      "Ein klarer Monatsplan",
      "Cinematic Reels & KI-Visuals",
      "Fertige Texte, die nach dir klingen",
      "Einheitlicher Auftritt auf Instagram & Google",
      "Mehr Vertrauen bei neuen Kunden",
      "Content, der regelmäßig veröffentlicht wird",
    ],
  },
  video: "/assets/videos/final.mp4",
  cta: "Content-Preview für meinen Betrieb anfragen",
};

export const pipeline = {
  eyebrow: "Production Pipeline",
  headline: "Von der Analyse zum laufenden System.",
  subline: "Vier Module, ein durchgehender Signalfluss — von der ersten Einschätzung bis zum monatlichen Posting.",
  steps: [
    { num: "01", title: "Analyse", body: "Wir scannen Branche, Angebot, Zielgruppe und deinen aktuellen Auftritt." },
    { num: "02", title: "Konzept", body: "Reel-Ideen, Tonalität und ein roter Faden, der zu deinem Betrieb passt." },
    { num: "03", title: "Content-Produktion", body: "Reels, KI-Visuals, Captions und Google-Beiträge — produziert und geprüft." },
    { num: "04", title: "Posting-System", body: "Monatsplan und Kalender, damit alles regelmäßig und planbar online geht." },
  ],
};

export interface Package {
  name: string;
  price: string;
  per: string;
  desc: string;
  features: string[];
  featured?: boolean;
}

/** Packages — exact prices preserved from the current site. */
export const packages = {
  eyebrow: "Monatspakete",
  headline: "Wähle, wie sichtbar dein Betrieb werden soll.",
  items: [
    {
      name: "Starter",
      price: "250€",
      per: "/ Monat",
      desc: "Für Betriebe, die endlich regelmäßig posten wollen, ohne jeden Tag neue Ideen suchen zu müssen.",
      features: [
        "8 Reel-Konzepte pro Monat",
        "12 fertige Captions",
        "4 Google-Beiträge",
        "1 klarer Monatsplan",
      ],
    },
    {
      name: "Wachstum",
      price: "490€",
      per: "/ Monat",
      desc: "Für Betriebe, die sichtbarer werden, professioneller auftreten und ihren Content klar planen lassen möchten.",
      featured: true,
      features: [
        "16 Reel-Konzepte pro Monat",
        "30 fertige Captions",
        "8 Google-Beiträge",
        "Bewertungsantworten",
        "Monatsplan + Strategie-Call",
      ],
    },
    {
      name: "Premium",
      price: "890€",
      per: "/ Monat",
      desc: "Für Betriebe, die ihren Content fast komplett auslagern und dauerhaft präsent bleiben wollen.",
      features: [
        "Unbegrenzte Reel-Konzepte",
        "60+ Captions pro Monat",
        "Tägliche Google-Beiträge",
        "Persönlicher Content-Ansprechpartner",
        "Priorisierter Support",
      ],
    },
  ] as Package[],
  notes: [
    "Du bekommst zuerst eine kurze Einschätzung, welches Paket zu deinem Betrieb passt. Keine direkte Zahlung auf der Website.",
    "Fertig produzierte Reels mit Schnitt, Untertiteln und Musik können zusätzlich angefragt werden.",
  ],
};

export interface AddOn {
  name: string;
  price: string;
  body: string;
}

/** Add-ons / Einzelaufträge — exact prices preserved. */
export const addOns = {
  eyebrow: "Einzelaufträge",
  headline: "Mehr als nur Content.",
  subline:
    "Du brauchst Website, Branding oder fertig produzierte Reels? Wir bauen deinen Auftritt weiter aus — mit klaren Festpreisen, sauberer Umsetzung und einem Ergebnis, das professionell wirkt.",
  items: [
    { name: "Website-Design", price: "ab 1.490€", body: "Eine moderne Website, die auf dem Handy stark aussieht, Vertrauen schafft und Kunden zur Anfrage bringt." },
    { name: "Logo & Branding", price: "ab 590€", body: "Ein sauberer Markenauftritt mit Logo, Farben und Schriften, damit dein Betrieb hochwertiger und einheitlicher wirkt." },
    { name: "Reel-Produktion", price: "ab 290€ / Reel", body: "Fertig geschnittene Reels mit Hook, Untertiteln, Musik und klarer Botschaft – bereit zum Veröffentlichen." },
    { name: "Social-Media-Setup", price: "ab 390€", body: "Wir optimieren dein Profil, deine Bio, Highlights und deinen ersten Content-Aufbau für einen starken Start." },
  ] as AddOn[],
  cta: "Projekt anfragen",
};

export const trust = {
  eyebrow: "Trust-Protokoll",
  headline: "Klarer Content statt Agentur-Blabla.",
  protocol: [
    { title: "Persönliche Content-Preview", body: "Du siehst zuerst, ob der Stil zu dir passt — bevor du dich entscheidest." },
    { title: "Monatlich kündbar", body: "Keine lange Bindung. Du bleibst jederzeit flexibel." },
    { title: "Direkter Kontakt per WhatsApp", body: "Kurze Wege statt komplizierter Agentur-Prozesse." },
    { title: "Klare Inhalte", body: "Verständlich und auf den Punkt — statt komplizierter Agentur-Sprache." },
  ],
};

export const faq = {
  eyebrow: "FAQ",
  headline: "Häufige Fragen.",
  items: [
    {
      q: "Für wen ist Cleanlines Studio geeignet?",
      a: "Für lokale Betriebe, die regelmäßig sichtbar sein wollen, aber keine Zeit haben, ständig Content zu planen, Texte zu schreiben oder neue Ideen zu suchen.",
    },
    {
      q: "Muss ich selbst filmen?",
      a: "Du kannst eigenes Material schicken oder die Ideen selbst mit dem Handy umsetzen. Auf Wunsch können fertig produzierte Reels zusätzlich angefragt werden.",
    },
    {
      q: "Macht ihr auch komplette Reels?",
      a: "Ja. Die Monatspakete enthalten vor allem Konzepte, Texte und Planung. Fertige Reels mit Schnitt, Untertiteln und Musik können als Zusatzleistung angefragt werden.",
    },
    {
      q: "Gibt es eine Mindestlaufzeit?",
      a: "Nein. Die Zusammenarbeit ist monatlich kündbar. Du kannst klein starten und später erweitern.",
    },
    {
      q: "Was passiert nach meiner Anfrage?",
      a: "Du schickst uns kurz deinen Betrieb, deine Branche und dein Ziel. Danach bekommst du eine erste Einschätzung und auf Wunsch eine kostenlose Content-Preview.",
    },
    {
      q: "Warum nicht einfach selbst mit KI machen?",
      a: "Weil die meisten Betriebe keine Zeit haben, jeden Tag gute Ideen, passende Texte und einen klaren Plan zu erstellen. Wir nehmen dir genau diese Arbeit ab und bereiten alles so vor, dass es zu deinem Betrieb passt.",
    },
  ],
};

export const finalCTA = {
  eyebrow: "Jetzt unverbindlich anfragen",
  headline: "Dein Betrieb kann aussehen wie eine Marke. Wir bauen den Content dafür.",
  subline:
    "Schick uns kurz deinen Betrieb und wir zeigen dir, welche Inhalte für dich funktionieren könnten — unverbindlich und ohne direkte Zahlung.",
  ctaPrimary: "Kostenlose Content-Preview anfragen",
  ctaSecondary: "WhatsApp-Anfrage starten",
  trust: ["Unverbindlich", "Persönlicher Kontakt", "Monatlich kündbar"],
  video: "/assets/videos/final.mp4",
};

export const nav = [
  { label: "Engine", target: "hero" },
  { label: "Diagnose", target: "diagnosis" },
  { label: "System", target: "content-os" },
  { label: "Reel Cinema", target: "reel-cinema" },
  { label: "Branchen", target: "industries" },
  { label: "Pakete", target: "packages" },
  { label: "Kontakt", target: "final-cta" },
];

export const preloader = {
  brand: "Cleanlines Studio",
  lines: [
    "Loading Content Engine",
    "Preparing Reel Cinema",
    "Calibrating Local Brand System",
    "Launching Cleanlines Studio",
  ],
};

/** Prefilled WhatsApp message reused across CTAs. */
export const waMessage =
  "Hallo Cleanlines Studio, ich möchte eine kostenlose Content-Preview anfragen.";
