/**
 * Cleanlines Studios — single source of truth.
 *
 * ┌─────────────────────────────────────────────────────────────────────┐
 * │  TODO BEFORE GOING LIVE — fill in the real contact details below.    │
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
  name: "Cleanlines Studios",
  short: "Cleanlines",
  tagline: "Content Engine für lokale Marken",
};

export const hero = {
  eyebrow: "Cinematic Content System · Lokale Betriebe",
  headline: "Dein Betrieb. So sichtbar wie eine große Marke.",
  subline:
    "Cinematic Reels, KI-Visuals und ein klares Content-System für lokale Betriebe, die online hochwertiger wirken, mehr Vertrauen aufbauen und regelmäßig neue Anfragen bekommen wollen.",
  ctaPrimary: "Kostenlos anfragen",
  ctaSecondary: "Beispiele ansehen",
  hud: {
    status: "CONTENT ENGINE ONLINE",
    pipeline: "REELS / AI VISUALS / SOCIAL PRESENCE",
    location: "MÜNCHEN / REMOTE / 24H PREVIEW",
  },
  trust: ["Unverbindlich", "persönlich", "monatlich kündbar"],
  stats: [
    { label: "Lokal", value: "Für lokale Betriebe gebaut" },
    { label: "Preview", value: "Persönliche Content-Preview" },
    { label: "Founder", value: "Angebot für die ersten Betriebe" },
  ],
};

export const diagnosis = {
  eyebrow: "Diagnose",
  headline: "Dein Betrieb ist stark. Nur online sieht man es nicht.",
  subline:
    "Viele lokale Betriebe leisten jeden Tag gute Arbeit. Aber auf Instagram, Google oder der Website wirkt es oft nicht so hochwertig, wie es in echt ist. Genau da setzen wir an – wir verwandeln deinen Betrieb in einen Auftritt, der Vertrauen schafft, auffällt und Kunden sofort zeigt: Hier bin ich richtig.",
  meters: [
    { label: "Sichtbarkeit", state: "zu wenig", value: 24 },
    { label: "Vertrauen", state: "ausbaufähig", value: 41 },
    { label: "Content-System", state: "fehlt", value: 8 },
  ],
  readouts: [
    "Posting unregelmäßig",
    "keine klare Linie",
    "wenig Anfragen",
    "wirkt nicht hochwertig",
  ],
};

export const contentOS = {
  eyebrow: "Content Operating System",
  headline: "Ein System statt einzelner Posts.",
  body: "Du bekommst nicht einfach ein Video. Du bekommst ein wiederholbares Content-System, das deinen Betrieb regelmäßig sichtbar macht — geplant in Themen, Formaten und Posting-Ideen, damit dein Auftritt nicht zufällig wirkt, sondern wie eine klare Marke.",
  core: "Cleanlines OS",
  modules: [
    "Content-Kalender",
    "Posting-Optionen",
    "Bewertungs-Verstärker",
    "KI-Visuals",
    "Google-Beiträge",
    "Captions",
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
  headline: "So kann dein Content aussehen.",
  subline:
    "Keine zufälligen Posts. Kein langweiliges Handyvideo ohne Wirkung. Wir bauen kurze, starke Content-Formate, die dein Angebot hochwertig zeigen und in Sekunden Aufmerksamkeit erzeugen.",
  reels: [
    { src: "/assets/videos/hero.mp4", title: "Brand Opener", meta: "SIGNATURE · Cinematic Einstieg", index: "01" },
    { src: "/assets/videos/reel-1.mp4", title: "Behind the Scenes", meta: "EINBLICK · Echte Arbeit", index: "02" },
    { src: "/assets/videos/show-1.mp4", title: "Produkt / Service Fokus", meta: "LEISTUNG · Klar erklärt", index: "03" },
    { src: "/assets/videos/reel-2.mp4", title: "Angebots-Reel", meta: "ANGEBOT · Verkauft ohne billig", index: "04" },
    { src: "/assets/videos/show-2.mp4", title: "Review / Trust Reel", meta: "TRUST · Kundenstimmen", index: "05" },
    { src: "/assets/videos/reel-3.mp4", title: "Brand Opener", meta: "HANDWERK · Vorher / Nachher", index: "06" },
    { src: "/assets/videos/show-3.mp4", title: "Behind the Scenes", meta: "GASTRO · Atmosphäre", index: "07" },
    { src: "/assets/videos/reel-4.mp4", title: "Produkt / Service Fokus", meta: "AUTO · Detailing", index: "08" },
    { src: "/assets/videos/show-4.mp4", title: "Review / Trust Reel", meta: "STUDIO · Ergebnisse", index: "09" },
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

/** Industries — six branches with tailored content angles. */
export const industries = {
  eyebrow: "Branchen",
  headline: "Content, der zu deinem Betrieb passt.",
  subline:
    "Jede Branche braucht andere Bilder, andere Worte und andere Kaufgründe. Ein Restaurant verkauft Atmosphäre. Ein Friseur verkauft Stil. Ein Handwerker verkauft Vertrauen. Ein Kosmetikstudio verkauft Ergebnis und Gefühl. Wir erstellen Content, der zu deinem Betrieb, deinen Kunden und deinem Angebot passt.",
  claims: ["Mehr Vertrauen", "Mehr Sichtbarkeit", "Mehr Anfragen", "Premium-Auftritt"],
  items: [
    {
      name: "Friseure",
      reel: "Vorher-Nachher, Transformationen, Styling, Vertrauen und Premium-Look.",
      caption: "Neuer Look, neues Gefühl – zeig, was mit dem richtigen Schnitt möglich ist.",
      google: "Neue Termine frei – sichere dir jetzt deinen Wunschtermin.",
      cta: "Wunschtermin sichern",
      metric: "Premium-Look",
      glow: "rgba(201,162,90,.55)",
      video: "/assets/videos/reel-1.mp4",
    },
    {
      name: "Restaurants",
      reel: "Food-Reels, Atmosphäre, Tagesgerichte, Reservierungsimpulse und lokale Sichtbarkeit.",
      caption: "Frisch, ehrlich, besonders – zeig, warum man heute bei dir essen sollte.",
      google: "Heute frisch gekocht – reservier deinen Tisch fürs Wochenende.",
      cta: "Tisch reservieren",
      metric: "Mehr Gäste",
      glow: "rgba(214,120,60,.5)",
      video: "/assets/videos/reel-2.mp4",
    },
    {
      name: "Handwerker",
      reel: "Saubere Arbeit, echte Ergebnisse, Baustellen-Einblicke und Vertrauen durch Kompetenz.",
      caption: "Kunden kaufen Vertrauen – zeig, wie sauber und sicher du arbeitest.",
      google: "Saubere Arbeit, faire Preise – jetzt unverbindliches Angebot anfordern.",
      cta: "Angebot anfordern",
      metric: "Mehr Vertrauen",
      glow: "rgba(70,120,190,.5)",
      video: "/assets/videos/reel-3.mp4",
    },
    {
      name: "Kosmetikstudios",
      reel: "Behandlungen, Ergebnisse, Studio-Vibe, Angebote und hochwertige Kundenansprache.",
      caption: "Deine Kunden buchen ein Gefühl von Pflege, Ruhe und Qualität.",
      google: "Gönn dir eine Auszeit – buche jetzt deine Wohlfühl-Behandlung.",
      cta: "Behandlung buchen",
      metric: "Mehr Wohlgefühl",
      glow: "rgba(206,108,150,.5)",
      video: "/assets/videos/show-1.mp4",
    },
    {
      name: "Fitness / Coaches",
      reel: "Transformation, Motivation, Expertise und klare Angebotskommunikation.",
      caption: "Keine Ausreden, kein kompliziertes Programm – nur ein klarer Start.",
      google: "Probetraining gratis – finde deinen Einstieg, der wirklich passt.",
      cta: "Probetraining sichern",
      metric: "Mehr Motivation",
      glow: "rgba(90,180,110,.5)",
      video: "/assets/videos/show-3.mp4",
    },
    {
      name: "Autopflege / Werkstatt",
      reel: "Details, Glanz, Prozesse, Ergebnisse und starke Vorher-Nachher-Clips.",
      caption: "Zeig den Unterschied, den echte Sorgfalt am Fahrzeug macht.",
      google: "Neue Termine verfügbar – bring deinen Wagen zum Glänzen.",
      cta: "Termin vereinbaren",
      metric: "Mehr Vertrauen",
      glow: "rgba(60,170,170,.5)",
      video: "/assets/videos/show-2.mp4",
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
  headline: "Von der Analyse zum laufenden Content-System.",
  subline:
    "Vom ersten Blick auf deinen Betrieb bis zum fertigen Content läuft alles klar, schnell und ohne komplizierte Agenturprozesse.",
  steps: [
    { num: "01", title: "Analyse", body: "Wir schauen uns deine Branche, dein Angebot, deine Zielgruppe und deinen aktuellen Online-Auftritt an." },
    { num: "02", title: "Konzept", body: "Wir entwickeln Content-Ideen, Botschaften und Formate, die zu deinem Betrieb passen und Kunden ansprechen." },
    { num: "03", title: "Content-Produktion", body: "Wir erstellen Reels, KI-Visuals, Captions und Google-Beiträge – fertig vorbereitet und einsatzbereit." },
    { num: "04", title: "Posting-System", body: "Du bekommst einen klaren Ablauf, damit dein Betrieb regelmäßig hochwertig sichtbar bleibt." },
    { num: "05", title: "Optimierung", body: "Wir schauen, was gut funktioniert, und verbessern Inhalte, Botschaften und Formate Schritt für Schritt." },
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
  subline:
    "Drei klare Pakete – je nachdem, ob du starten, wachsen oder deinen Auftritt komplett auf Premium bringen willst.",
  items: [
    {
      name: "Starter",
      price: "250€",
      per: "/ Monat",
      desc: "Für Betriebe, die endlich regelmäßig sichtbar werden wollen, ohne direkt ein großes Paket zu buchen.",
      features: [
        "8 Reel-Konzepte pro Monat",
        "12 fertige Captions",
        "4 Google-Beiträge",
        "1 klarer Monatsplan",
        "WhatsApp-Abstimmung",
        "monatlich kündbar",
      ],
    },
    {
      name: "Wachstum",
      price: "490€",
      per: "/ Monat",
      desc: "Für Betriebe, die sichtbarer, professioneller und aktiver auf Social Media auftreten wollen.",
      featured: true,
      features: [
        "16 Reel-Konzepte pro Monat",
        "30 fertige Captions",
        "8 Google-Beiträge",
        "Bewertungs- und Vertrauens-Content",
        "Monatsplan + Strategie-Call",
        "Content-Ideen passend zu deiner Branche",
        "WhatsApp-Support",
      ],
    },
    {
      name: "Premium",
      price: "890€",
      per: "/ Monat",
      desc: "Für Betriebe, die ihren Content-Auftritt ernsthaft auf Marken-Niveau bringen wollen.",
      features: [
        "Unbegrenzte Reel-Konzepte im Rahmen des Monatsplans",
        "60+ Captions pro Monat",
        "Tägliche Google-Beiträge möglich",
        "Persönlicher Content-Ansprechpartner",
        "KI-Visuals & Premium-Assets",
        "Review- und Angebotskampagnen",
        "Prioritäts-Support",
        "Monatliche Optimierung",
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

/** Add-ons / Einzelaufträge. */
export const addOns = {
  eyebrow: "Mehr als Content",
  headline: "Mehr als nur Content.",
  subline:
    "Dein Auftritt besteht nicht nur aus Reels. Website, Branding, Google, Bewertungen und Social Media müssen zusammenpassen, damit Kunden dir schneller vertrauen.",
  items: [
    { name: "Website-Design", price: "ab 1.400€", body: "Eine moderne Website, die auf dem Handy stark aussieht, Vertrauen schafft und Anfragen leichter macht." },
    { name: "Logo & Branding", price: "ab 650€", body: "Ein sauberer Markenauftritt mit Logo, Farben und Schriften, damit dein Betrieb hochwertiger und einheitlicher wirkt." },
    { name: "Reel-Produktion", price: "ab 250€ / Reel", body: "Fertig geschnittene Reels mit Hook, Untertiteln, Musik und klarer Botschaft – bereit zum Veröffentlichen." },
    { name: "Social-Media-System", price: "monatlich buchbar", body: "Wir strukturieren deinen Auftritt, planen Inhalte und sorgen dafür, dass dein Betrieb regelmäßig sichtbar bleibt." },
    { name: "Google Business Optimierung", price: "ab 350€", body: "Beiträge, Bilder, Texte und Bewertungsimpulse für mehr Vertrauen bei lokaler Suche." },
  ] as AddOn[],
  cta: "Projekt anfragen",
};

export const trust = {
  eyebrow: "Trust-Protokoll",
  headline: "Klarer Content. Kein Agentur-Blabla.",
  body: "Du bekommst keine komplizierten Strategien, die am Ende keiner umsetzt. Du bekommst klare Inhalte, klare Abläufe und Content, der deinen Betrieb hochwertig zeigt.",
  protocol: [
    { title: "Persönliche Content-Preview", body: "Du siehst vorher, welche Richtung für deinen Betrieb Sinn macht – bevor du dich entscheidest." },
    { title: "Monatlich kündbar", body: "Keine lange Bindung. Du bleibst flexibel und entscheidest jeden Monat neu." },
    { title: "Direkter Kontakt per WhatsApp", body: "Kurze Wege, schnelle Abstimmung und keine unnötigen Meetings." },
    { title: "Klare Inhalte", body: "Verständlich, hochwertig und auf den Punkt – statt komplizierter Agentur-Sprache." },
  ],
};

export const faq = {
  eyebrow: "FAQ",
  headline: "Häufige Fragen.",
  items: [
    {
      q: "Für wen ist Cleanlines Studio geeignet?",
      a: "Für lokale Betriebe, die online sichtbarer, hochwertiger und vertrauenswürdiger wirken wollen – ohne selbst ständig Content planen, filmen oder schneiden zu müssen.",
    },
    {
      q: "Muss ich selbst filmen?",
      a: "Nicht unbedingt. Je nach Paket arbeiten wir mit vorhandenem Material, KI-Visuals, Bildern, kurzen Clips oder klaren Content-Vorlagen.",
    },
    {
      q: "Macht ihr auch komplette Reels?",
      a: "Ja. Wir erstellen Reels mit Hook, Schnitt, Text, Musikgefühl, Caption und klarer Botschaft.",
    },
    {
      q: "Gibt es eine Mindestlaufzeit?",
      a: "Nein. Du kannst monatlich kündigen und erstmal testen, ob das System zu deinem Betrieb passt.",
    },
    {
      q: "Was passiert nach meiner Anfrage?",
      a: "Du schickst uns kurz deinen Betrieb, deine Branche und dein Ziel. Danach bekommst du eine Einschätzung, welche Inhalte für dich am meisten Sinn machen.",
    },
    {
      q: "Warum nicht einfach selbst mit KI machen?",
      a: "Weil gute KI-Inhalte nicht durch Tools entstehen, sondern durch Konzept, Stilgefühl, Auswahl, Text, Aufbau und saubere Umsetzung. Genau das übernehmen wir.",
    },
  ],
};

export const finalCTA = {
  eyebrow: "Jetzt unverbindlich anfragen",
  headline: "Dein Betrieb kann aussehen wie eine Marke. Wir bauen den Content dafür.",
  subline:
    "Schick uns kurz deinen Betrieb und wir zeigen dir, welche Inhalte für dich funktionieren können – unverbindlich, direkt und ohne komplizierten Agenturprozess.",
  ctaPrimary: "Kostenlos anfragen",
  ctaSecondary: "WhatsApp-Anfrage starten",
  trust: ["Unverbindlich", "klare Einschätzung", "keine versteckten Kosten"],
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
  brand: "Cleanlines Studios",
  lines: [
    "Loading Content Engine",
    "Preparing Reel Cinema",
    "Calibrating Local Brand System",
    "Launching Cleanlines Studios",
  ],
};

/** Prefilled WhatsApp message reused across CTAs. */
export const waMessage =
  "Hallo Cleanlines Studios, ich möchte eine kostenlose Content-Preview anfragen.";
