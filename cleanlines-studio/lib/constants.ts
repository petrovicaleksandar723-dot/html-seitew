export const NAV_LINKS = [
  { label: "Engine", href: "#hero" },
  { label: "Diagnose", href: "#diagnose" },
  { label: "System", href: "#system" },
  { label: "Reel Cinema", href: "#reel-cinema" },
  { label: "Branchen", href: "#branchen" },
  { label: "Pakete", href: "#pakete" },
  { label: "Kontakt", href: "#kontakt" },
] as const;

export const DIAGNOSIS_METRICS = [
  { label: "Sichtbarkeit", value: "zu schwach", level: 0.28 },
  { label: "Vertrauen", value: "nicht stark genug", level: 0.46 },
  { label: "Content-System", value: "fehlt", level: 0.12 },
] as const;

export const DIAGNOSIS_TAGS = [
  "unregelmäßige Posts",
  "kein klarer Look",
  "zu wenig Vertrauen",
  "zu wenige Anfragen",
  "Auftritt wirkt kleiner als der Betrieb wirklich ist",
] as const;

export const TRANSFORM_BEFORE = [
  "unregelmäßige Inhalte",
  "kein einheitlicher Look",
  "wenig Vertrauen",
  "Kunden verstehen den Wert nicht sofort",
  "Anfragen gehen an andere",
] as const;

export const TRANSFORM_AFTER = [
  "klare Botschaft",
  "hochwertiger Content",
  "professioneller Auftritt",
  "mehr Vertrauen vor der Anfrage",
  "lokaler Betrieb wirkt wie Marke",
] as const;

export const REELS = [
  {
    n: "01",
    title: "Brand Opener",
    body: "Ein starker Einstieg, der deinen Betrieb sofort professioneller, größer und einprägsamer wirken lässt.",
  },
  {
    n: "02",
    title: "Behind the Scenes",
    body: "Echte Einblicke in deine Arbeit — hochwertig geschnitten, spannend aufgebaut und nahbar erzählt.",
  },
  {
    n: "03",
    title: "Produkt / Service Fokus",
    body: "Deine Leistung klar erklärt, visuell stark inszeniert und für neue Kunden sofort verständlich.",
  },
  {
    n: "04",
    title: "Angebots-Reel",
    body: "Ein kurzer Clip, der dein Angebot sichtbar macht, ohne billig oder aufdringlich zu wirken.",
  },
  {
    n: "05",
    title: "Review / Trust Reel",
    body: "Bewertungen, Ergebnisse und Kundenstimmen so aufbereitet, dass sie Vertrauen schaffen, bevor jemand anfragt.",
  },
] as const;

export const OS_MODULES = [
  {
    title: "Content-Kalender",
    body: "Du weißt vorher, was kommt. Kein Stress, kein spontanes Chaos, keine leeren Ideen.",
  },
  {
    title: "Posting-Optionen",
    body: "Fertige Inhalte für Instagram, TikTok, Google und deinen lokalen Auftritt.",
  },
  {
    title: "Bewertungs-Verstärker",
    body: "Content, der Vertrauen aufbaut und zeigt, warum Kunden bei dir richtig sind.",
  },
  {
    title: "KI-Visuals",
    body: "Hochwertige Visuals für Angebote, Reels, Stories und starke Markenmomente.",
  },
  {
    title: "Google-Beiträge",
    body: "Damit dein Betrieb nicht nur gut aussieht, sondern auch lokal präsenter wirkt.",
  },
  {
    title: "Captions",
    body: "Texte, die menschlich klingen, klar verkaufen und nicht nach KI oder Agentur-Blabla wirken.",
  },
] as const;

export const INDUSTRIES = [
  {
    title: "Friseure",
    body: "Vorher-Nachher, Transformationen, Styling, Persönlichkeit und Premium-Look.",
    accent: "#d8b274",
  },
  {
    title: "Restaurants",
    body: "Food-Reels, Atmosphäre, Tagesgerichte, Reservierungsimpulse und lokale Sichtbarkeit.",
    accent: "#e0915f",
  },
  {
    title: "Handwerker",
    body: "Saubere Arbeit, echte Ergebnisse, Baustellen-Einblicke und Vertrauen durch Kompetenz.",
    accent: "#c9b083",
  },
  {
    title: "Kosmetikstudios",
    body: "Behandlungen, Ergebnisse, Studio-Vibe, Angebote und hochwertige Kundenansprache.",
    accent: "#deb6a0",
  },
  {
    title: "Fitness / Coaches",
    body: "Transformation, Motivation, Expertise und klare Angebotskommunikation.",
    accent: "#cdbf9a",
  },
  {
    title: "Autopflege / Werkstatt",
    body: "Details, Glanz, Prozesse, Ergebnisse und starke Vorher-Nachher-Clips.",
    accent: "#b8b6ad",
  },
] as const;

export const PIPELINE = [
  {
    n: "01",
    title: "Analyse",
    body: "Wir schauen uns deine Branche, dein Angebot, deine Zielgruppe und deinen aktuellen Online-Auftritt an.",
  },
  {
    n: "02",
    title: "Konzept",
    body: "Wir entwickeln Content-Ideen, Botschaften und Formate, die zu deinem Betrieb passen und Kunden ansprechen.",
  },
  {
    n: "03",
    title: "Produktion",
    body: "Wir erstellen Reels, KI-Visuals, Captions und Google-Beiträge — fertig vorbereitet und einsatzbereit.",
  },
  {
    n: "04",
    title: "Posting-System",
    body: "Du bekommst einen klaren Monatsplan, damit dein Betrieb regelmäßig hochwertig sichtbar bleibt.",
  },
  {
    n: "05",
    title: "Optimierung",
    body: "Wir prüfen, was gut funktioniert, und verbessern Inhalte, Botschaften und Formate Schritt für Schritt.",
  },
] as const;

export const SERVICES = [
  {
    title: "Website-Design",
    body: "Eine moderne Website, die auf dem Handy stark aussieht, Vertrauen schafft und Anfragen leichter macht.",
    price: "ab 1.400€",
  },
  {
    title: "Logo & Branding",
    body: "Ein sauberer Markenauftritt mit Logo, Farben und Schriften, damit dein Betrieb hochwertiger und einheitlicher wirkt.",
    price: "ab 650€",
  },
  {
    title: "Reel-Produktion",
    body: "Fertig geschnittene Reels mit Hook, Untertiteln, Musikgefühl und klarer Botschaft — bereit zum Veröffentlichen.",
    price: "ab 250€ / Reel",
  },
  {
    title: "Social-Media-System",
    body: "Wir strukturieren deinen Auftritt, planen Inhalte und sorgen dafür, dass dein Betrieb regelmäßig sichtbar bleibt.",
    price: "monatlich buchbar",
  },
  {
    title: "Google Business Optimierung",
    body: "Beiträge, Bilder, Texte und Bewertungsimpulse für mehr Vertrauen bei lokaler Suche.",
    price: "ab 350€",
  },
] as const;

export const PLANS = [
  {
    name: "Starter",
    price: "250€",
    cadence: "/ Monat",
    blurb:
      "Für Betriebe, die regelmäßig sichtbar werden wollen, ohne direkt ein großes Paket zu buchen.",
    features: [
      "8 Reel-Konzepte pro Monat",
      "12 fertige Captions",
      "4 Google-Beiträge",
      "1 klarer Monatsplan",
      "WhatsApp-Abstimmung",
      "monatlich kündbar",
    ],
    cta: "Starter anfragen",
    featured: false,
  },
  {
    name: "Wachstum",
    price: "490€",
    cadence: "/ Monat",
    blurb:
      "Für Betriebe, die sichtbarer, professioneller und aktiver auf Social Media auftreten wollen.",
    features: [
      "16 Reel-Konzepte pro Monat",
      "30 fertige Captions",
      "8 Google-Beiträge",
      "Bewertungs- und Vertrauens-Content",
      "Monatsplan + Strategie-Call",
      "Content-Ideen passend zu deiner Branche",
      "WhatsApp-Support",
    ],
    cta: "Wachstum anfragen",
    featured: true,
  },
  {
    name: "Premium",
    price: "890€",
    cadence: "/ Monat",
    blurb:
      "Für Betriebe, die ihren Content-Auftritt ernsthaft auf Marken-Niveau bringen wollen.",
    features: [
      "unbegrenzte Reel-Konzepte im Rahmen des Monatsplans",
      "60+ Captions pro Monat",
      "tägliche Google-Beiträge möglich",
      "persönlicher Content-Ansprechpartner",
      "KI-Visuals & Premium-Assets",
      "Review- und Angebotskampagnen",
      "Prioritäts-Support",
      "monatliche Optimierung",
    ],
    cta: "Premium anfragen",
    featured: false,
  },
] as const;

export const TRUST = [
  "Persönliche Content-Preview vor dem Start",
  "Monatlich kündbar",
  "Direkter Kontakt per WhatsApp",
  "Klare Inhalte statt Agentur-Blabla",
] as const;

export const FAQ = [
  {
    q: "Für wen ist Cleanlines Studio geeignet?",
    a: "Für lokale Betriebe, die online sichtbarer, hochwertiger und vertrauenswürdiger wirken wollen — ohne selbst ständig Content planen, filmen oder schneiden zu müssen.",
  },
  {
    q: "Muss ich selbst filmen?",
    a: "Nicht unbedingt. Je nach Paket arbeiten wir mit vorhandenem Material, KI-Visuals, Bildern, kurzen Clips oder klaren Content-Vorlagen.",
  },
  {
    q: "Macht ihr auch komplette Reels?",
    a: "Ja. Wir erstellen Reels mit Hook, Schnitt, Untertiteln, Musikgefühl, Caption und klarer Botschaft.",
  },
  {
    q: "Gibt es eine Mindestlaufzeit?",
    a: "Nein. Du kannst monatlich kündigen und erstmal testen, ob das System zu deinem Betrieb passt.",
  },
  {
    q: "Was passiert nach meiner Anfrage?",
    a: "Du schickst uns kurz deinen Betrieb, deine Branche und dein Ziel. Danach bekommst du eine klare Einschätzung, welche Inhalte für dich am meisten Sinn machen.",
  },
  {
    q: "Warum nicht einfach selbst mit KI machen?",
    a: "Weil starke Inhalte nicht nur durch Tools entstehen. Entscheidend sind Konzept, Stil, Hook, Auswahl, Text und saubere Umsetzung. Genau das übernehmen wir.",
  },
] as const;
