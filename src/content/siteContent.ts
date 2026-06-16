/* ============================================================
   CLEANLINES STUDIO — single source of truth for all content
   ============================================================ */

export const CONTACT = {
  // ← TODO: vor dem Live-Gang durch echte Werte ersetzen
  email: "cleanlinesstudio@example.com",
  whatsapp: "49XXXXXXXXXX", // Format 49..., ohne + / Leerzeichen
  city: "München",
};

export function mailtoHref(subject: string, body?: string): string {
  const q = `subject=${encodeURIComponent(subject)}${
    body ? `&body=${encodeURIComponent(body)}` : ""
  }`;
  return `mailto:${CONTACT.email}?${q}`;
}

export function whatsappHref(text: string): string {
  return `https://wa.me/${CONTACT.whatsapp}?text=${encodeURIComponent(text)}`;
}

export const NAV = [
  { id: "problem", label: "Diagnose" },
  { id: "system", label: "System" },
  { id: "showcase", label: "Showcase" },
  { id: "industries", label: "Branchen" },
  { id: "process", label: "Ablauf" },
  { id: "packages", label: "Pakete" },
];

export const PRELOADER_LINES = [
  "Loading Content Engine",
  "Preparing Reel Cinema",
  "Calibrating Local Brand System",
  "Launching CleanLines Studio",
];

export const HERO = {
  hud: "Content Engine online",
  tickerTop: "Local Business → Premium Content System",
  tickerMid: "Reels / AI Visuals / Social Presence",
  tickerLow: "München / Remote / 24H Preview",
  headline: ["Dein Betrieb.", "Als wäre er", "eine große Marke."],
  gold: "eine große Marke.",
  subline:
    "Cinematic Reels, KI-Visuals und Content-Systeme für lokale Betriebe, die online endlich hochwertig wirken wollen.",
  primary: "Content-Preview sichern",
  secondary: "Showcase ansehen",
  stats: [
    { value: "24h", label: "Erste Preview" },
    { value: "0 €", label: "Einrichtung" },
    { value: "100%", label: "Auf dich abgestimmt" },
  ],
};

export const MARQUEE = [
  "Cinematic Reels",
  "KI-Visuals",
  "Content-Systeme",
  "Google-Beiträge",
  "Social Presence",
  "Kampagnen",
];

export const DIAGNOSIS = {
  label: "01 — Diagnose",
  headline: "Dein Betrieb ist gut. Aber online sieht man es nicht.",
  gold: "online sieht man es nicht.",
  lede: "Dein Betrieb wirkt online nur so hochwertig wie dein Content. Gute Arbeit allein reicht nicht — wirkt der erste Eindruck im Feed beliebig, entscheiden sich Kunden für jemand anderen.",
  modules: [
    { k: "A", title: "Kein klarer erster Eindruck", desc: "Profil und Feed verkaufen deinen Standard nicht." },
    { k: "B", title: "Content wirkt beliebig", desc: "Posten, um irgendwas zu posten — ohne System." },
    { k: "C", title: "Keine Wiedererkennung", desc: "Kein roter Faden, keine Marke, keine Erinnerung." },
  ],
  meters: [
    { label: "Sichtbarkeit", value: 22, display: "niedrig", tone: "low" as const },
    { label: "Vertrauen / erster Eindruck", value: 34, display: "unklar", tone: "low" as const },
    { label: "Wiedererkennung", value: 48, display: "48%", tone: "mid" as const },
    { label: "Content-System aktiv", value: 12, display: "fehlt", tone: "low" as const },
  ],
  status: "Diagnose: starke Arbeit, schwacher Auftritt — System fehlt.",
};

export const OS = {
  label: "Das System",
  headline: "Kein einzelnes Video. Ein Content-System.",
  gold: "Ein Content-System.",
  lede: "Du bekommst kein einzelnes Video. Du bekommst ein System, das deinen Betrieb regelmäßig hochwertig sichtbar macht — Modul für Modul, jeden Monat fertig.",
  core: { title: "CleanLines OS", desc: "Alle Module laufen in einem System zusammen — geplant, konsistent, sendefertig." },
  modules: [
    { n: "M01", title: "Cinematic Reels", desc: "Wort-für-Wort-Skripte mit Hook, Ablauf und CTA." },
    { n: "M02", title: "KI-Visuals", desc: "Premium-Bilder, die deinen Feed sofort hochwertiger wirken lassen." },
    { n: "M03", title: "Google-Beiträge", desc: "Lokal optimiert, damit dich Kunden aus deiner Stadt finden." },
    { n: "M04", title: "Captions", desc: "Sendefertige Texte, die nach dir klingen — nicht nach KI." },
    { n: "M05", title: "Monatsplan", desc: "Du weißt vorab, was wann online geht. Übersicht statt Chaos." },
    { n: "M06", title: "Bewertungsantworten", desc: "Professionelle Antworten, die Vertrauen aufbauen." },
    { n: "M07", title: "Posting-System", desc: "Du postest in Minuten statt Stunden." },
    { n: "M08", title: "Content-Kalender", desc: "Ein roter Faden über den ganzen Monat." },
  ],
};

export type Reel = {
  video: string;
  industry: string;
  title: string;
  outcome: string;
};

export const REELS: Reel[] = [
  { video: "/assets/videos/show-1.mp4", industry: "Restaurant", title: "Signature-Dish Reel", outcome: "Mehr Reservierungen unter der Woche." },
  { video: "/assets/videos/reel-1.mp4", industry: "Barber", title: "Cut & Fade Transformation", outcome: "Volle Stühle durch Online-Buchung." },
  { video: "/assets/videos/show-2.mp4", industry: "Gym / Fitness", title: "Membership-Kampagne", outcome: "Planbar neue Anmeldungen." },
  { video: "/assets/videos/reel-2.mp4", industry: "Car Detailer", title: "Keramik-Glanz Visual", outcome: "Hochwertige Aufbereitungs-Anfragen." },
  { video: "/assets/videos/show-3.mp4", industry: "Café", title: "Launch-Film", outcome: "Lokale Reichweite zum Start." },
  { video: "/assets/videos/reel-3.mp4", industry: "Beauty / Studio", title: "Premium Brand-Clip", outcome: "Vertrauen, das Termine bucht." },
  { video: "/assets/videos/show-4.mp4", industry: "Handwerk", title: "Projekt-Film", outcome: "Qualifizierte Anfragen aus der Region." },
];

export type Industry = {
  id: string;
  name: string;
  tag: string;
  title: string;
  desc: string;
  hue: string; // base radial color
};

export const INDUSTRIES: Industry[] = [
  { id: "friseure", name: "Friseure", tag: "Auslastung", title: "Wir füllen leere Stühle", desc: "Reels, die deine Cuts und Fades zeigen, Google-Beiträge für freie Termine und Story-Konzepte für deine Online-Buchung.", hue: "#241a12" },
  { id: "restaurants", name: "Restaurants", tag: "Reservierungen", title: "Volle Tische, auch unter der Woche", desc: "Appetitstarke Reels zu deinen Spezialitäten, Wochenkarten-Beiträge und Story-Konzepte, die schon mittags Lust auf den Abend machen.", hue: "#2a1a10" },
  { id: "handwerker", name: "Handwerker", tag: "Expertenstatus", title: "Lokaler Expertenstatus", desc: "Projekte verständlich aufbereitet, regionale Google-Beiträge und dein Team im Einsatz — für qualifizierte Anfragen aus der Umgebung.", hue: "#1f1810" },
  { id: "kosmetik", name: "Kosmetikstudios", tag: "Vertrauen", title: "Content, der Vertrauen aufbaut", desc: "Echte Behandlungsvorteile statt Floskeln: Vorher/Nachher-Ideen, Pflege-Tipps, FAQ-Posts und Reels für Treatments.", hue: "#251a13" },
  { id: "auto", name: "Autohäuser", tag: "Premium-Aufträge", title: "Mach den Unterschied sichtbar", desc: "Cinematic Fahrzeug-Clips, Premium-Visuals und Angebots-Beiträge, die hochwertige Anfragen bringen.", hue: "#1d1610" },
  { id: "fitness", name: "Fitnessstudios", tag: "Anmeldungen", title: "Planbar neue Mitglieder", desc: "Motivierende Kampagnen, Transformation-Reels und Aktions-Beiträge, die deine Probetrainings füllen.", hue: "#22180f" },
  { id: "cafes", name: "Cafés", tag: "Reichweite", title: "Lokale Reichweite zum Launch", desc: "Atmosphärische Clips, Specials und Beiträge, die Laufkundschaft aus deiner Nachbarschaft holen.", hue: "#241b11" },
  { id: "kliniken", name: "Kliniken", tag: "Seriosität", title: "Seriös und nahbar zugleich", desc: "Aufklärungs-Content, FAQ-Beiträge und ein Auftritt, der Kompetenz zeigt und Patienten Sicherheit gibt.", hue: "#1b1510" },
  { id: "immobilien", name: "Immobilien", tag: "Premium-Auftritt", title: "Objekte, die hochwertig wirken", desc: "Cinematic Objekt-Clips, Premium-Visuals und Beiträge, die Eigentümer und Käufer gleichermaßen überzeugen.", hue: "#241b12" },
];

export const TRANSFORMATION = {
  before: {
    state: "Vorher · ohne System",
    headline: "Gute Arbeit, schwacher Auftritt.",
    list: ["Unregelmäßige Posts", "Keine klare Linie", "Wenig Vertrauen", "Social Media bleibt liegen"],
  },
  after: {
    state: "Nachher · mit CleanLines",
    headline: "Ein Auftritt, der Vertrauen verkauft.",
    gold: "Vertrauen verkauft.",
    list: ["Klarer Monatsplan", "Cinematic Reels", "Einheitlicher Auftritt", "Mehr Vertrauen"],
  },
};

export const PIPELINE = {
  label: "Ablauf",
  headline: "Die Produktions-Pipeline.",
  gold: "Produktions-Pipeline.",
  steps: [
    { n: "01", title: "Analyse", desc: "Branche, Angebot und Ziele — wir verstehen deinen Betrieb in Minuten." },
    { n: "02", title: "Konzept", desc: "Wir bauen dein Content-System: Themen, Hooks, roter Faden, Plan." },
    { n: "03", title: "Content-Produktion", desc: "Reels-Skripte, KI-Visuals und Beiträge — premium und sendefertig." },
    { n: "04", title: "Posting-System", desc: "Mit Kalender online — du postest in Minuten, Feedback verfeinert alles." },
  ],
};

export type Package = {
  id: string;
  name: string;
  price: string;
  desc: string;
  features: string[];
  featured?: boolean;
};

export const PACKAGES: Package[] = [
  {
    id: "Starter",
    name: "Starter",
    price: "250 €",
    desc: "Für Betriebe, die endlich regelmäßig posten wollen, ohne jeden Tag neue Ideen suchen zu müssen.",
    features: ["8 Reel-Konzepte pro Monat", "12 fertige Captions", "4 Google-Beiträge", "1 klarer Monatsplan"],
  },
  {
    id: "Wachstum",
    name: "Wachstum",
    price: "490 €",
    desc: "Für Betriebe, die sichtbarer werden, professioneller auftreten und ihren Content klar planen lassen möchten.",
    features: ["16 Reel-Konzepte pro Monat", "30 fertige Captions", "8 Google-Beiträge", "Bewertungsantworten", "Monatsplan + Strategie-Call"],
    featured: true,
  },
  {
    id: "Premium",
    name: "Premium",
    price: "890 €",
    desc: "Für Betriebe, die ihren Content fast komplett auslagern und dauerhaft präsent bleiben wollen.",
    features: ["Unbegrenzte Reel-Konzepte", "60+ Captions pro Monat", "Tägliche Google-Beiträge", "Persönlicher Content-Ansprechpartner", "Priorisierter Support"],
  },
];

export const ADDONS = [
  { title: "Website-Design", price: "ab 1.490 €", desc: "Eine moderne Website, die auf dem Handy stark aussieht, Vertrauen schafft und Kunden zur Anfrage bringt." },
  { title: "Logo & Branding", price: "ab 590 €", desc: "Ein sauberer Markenauftritt mit Logo, Farben und Schriften — hochwertiger und einheitlicher." },
  { title: "Reel-Produktion", price: "ab 290 € / Reel", desc: "Fertig geschnittene Reels mit Hook, Untertiteln, Musik und klarer Botschaft — bereit zum Posten." },
  { title: "Social-Media-Setup", price: "ab 390 €", desc: "Profil, Bio, Highlights und erster Content-Aufbau für einen starken Start." },
];

export const TRUST = [
  "Persönliche Content-Preview vor dem Start",
  "Monatlich kündbar, keine lange Bindung",
  "Direkter Kontakt per WhatsApp",
  "Klare Inhalte statt Agentur-Blabla",
];

export const FAQ = [
  { q: "Muss ich selbst filmen?", a: "Du kannst eigenes Material schicken oder die Ideen selbst mit dem Handy umsetzen — dafür bekommst du ein Wort-für-Wort-Skript. Auf Wunsch produzieren wir fertige Reels als Zusatzleistung." },
  { q: "Gibt es eine Mindestlaufzeit?", a: "Nein. Die Zusammenarbeit ist monatlich kündbar. Du kannst klein starten und später erweitern." },
  { q: "Werden die Texte für meinen Standort optimiert?", a: "Ja. Wir bauen deinen Standort und branchenrelevante Suchbegriffe gezielt in die Beiträge ein (Local SEO), damit dein Betrieb regional besser gefunden wird." },
  { q: "Wie schnell bekomme ich mein erstes Paket?", a: "Eine erste Content-Preview gibt es in der Regel innerhalb von 24 Stunden. Dein erstes volles Monats-Paket folgt innerhalb weniger Werktage." },
  { q: "Warum nicht einfach selbst mit KI machen?", a: "Weil die meisten Betriebe keine Zeit haben, täglich gute Ideen, passende Texte und einen klaren Plan zu erstellen. Genau diese Arbeit nehmen wir dir ab — abgestimmt auf deinen Betrieb." },
];

export const FINAL = {
  label: "Kostenlose Preview",
  headline: ["Dein Betrieb kann aussehen wie eine Marke.", "Wir bauen den Content dafür."],
  gold: "Wir bauen den Content dafür.",
  sub: "Schick uns kurz deinen Betrieb und wir zeigen dir, welche Inhalte für dich funktionieren — unverbindlich, ohne Abo, ohne Risiko.",
  primary: "Kostenlose Content-Preview anfragen",
  whatsapp: "WhatsApp-Anfrage starten",
};
