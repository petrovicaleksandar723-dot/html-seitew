import { asset } from "@/lib/asset";

export const IMG = {
  hero: asset("/images/hero.jpg"),
  owner: asset("/images/owner.jpg"),
  reels: asset("/images/reels.jpg"),
  photographer: asset("/images/photographer.jpg"),
  restaurant: asset("/images/restaurant.jpg"),
  fitness: asset("/images/fitness.jpg"),
  beauty: asset("/images/beauty.jpg"),
  skyline: asset("/images/skyline.jpg"),
};

export const SERVICES = [
  {
    n: "01",
    title: "Reels & Short-Form",
    body: "Scroll-stoppende Vertical-Videos, die deinen Betrieb in Bewegung zeigen — gedreht, geschnitten und veröffentlichungsfertig.",
    image: IMG.reels,
  },
  {
    n: "02",
    title: "Foto & Produkt",
    body: "Hochwertige Bildwelten, die deine Arbeit so premium aussehen lassen, wie sie wirklich ist. Studio- und Vor-Ort-Produktion.",
    image: IMG.photographer,
  },
];

export const INDUSTRIES = [
  {
    title: "Gastronomie",
    body: "Atmosphäre, die Appetit macht — und Tische füllt.",
    image: IMG.restaurant,
  },
  {
    title: "Fitness",
    body: "Energie und Disziplin, sichtbar gemacht. Mehr Probetrainings.",
    image: IMG.fitness,
  },
  {
    title: "Beauty",
    body: "Eleganz, die Vertrauen schafft und Termine bringt.",
    image: IMG.beauty,
  },
];

export const STEPS = [
  {
    n: "01",
    title: "Analyse",
    body: "Wir schauen uns deinen Auftritt an und finden, was dich wirklich verkauft.",
  },
  {
    n: "02",
    title: "Konzept",
    body: "Ein klarer Plan: Formate, Tonalität und Themen, die zu deinem Betrieb passen.",
  },
  {
    n: "03",
    title: "Produktion",
    body: "Wir drehen und gestalten Content auf Premium-Niveau — unkompliziert für dich.",
  },
  {
    n: "04",
    title: "Wachstum",
    body: "Laufend frischer Content, der Sichtbarkeit und Anfragen aufbaut.",
  },
];

export const PLANS = [
  {
    name: "Start",
    price: "890 €",
    cadence: "/ Monat",
    blurb: "Für Betriebe, die endlich sichtbar werden wollen.",
    features: ["4 Reels / Monat", "Foto-Set", "Content-Plan", "Veröffentlichung"],
    featured: false,
    cta: "Anfragen",
  },
  {
    name: "Wachstum",
    price: "1.490 €",
    cadence: "/ Monat",
    blurb: "Der Standard für konstante Premium-Präsenz.",
    features: [
      "8 Reels / Monat",
      "Foto- & Produkt-Shooting",
      "Strategie & Themenplan",
      "Google & Social",
      "Monatliches Reporting",
    ],
    featured: true,
    cta: "Anfragen",
  },
  {
    name: "Premium",
    price: "ab 2.490 €",
    cadence: "/ Monat",
    blurb: "Maximale Sichtbarkeit für ambitionierte Marken.",
    features: [
      "12+ Reels / Monat",
      "Volle Produktion",
      "Kampagnen & Ads",
      "Dedizierter Ansprechpartner",
    ],
    featured: false,
    cta: "Anfragen",
  },
];
