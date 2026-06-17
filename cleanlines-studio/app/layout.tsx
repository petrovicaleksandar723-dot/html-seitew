import type { Metadata, Viewport } from "next";
import {
  Hanken_Grotesk,
  DM_Sans,
  Instrument_Serif,
  JetBrains_Mono,
} from "next/font/google";
import "./globals.css";
import SmoothScroll from "@/components/smooth-scroll";

const hanken = Hanken_Grotesk({
  subsets: ["latin"],
  weight: ["400", "500", "700", "800"],
  variable: "--font-hanken",
  display: "swap",
});
const dm = DM_Sans({
  subsets: ["latin"],
  weight: ["400", "500"],
  variable: "--font-dm",
  display: "swap",
});
const instrument = Instrument_Serif({
  subsets: ["latin"],
  weight: ["400"],
  style: ["italic", "normal"],
  variable: "--font-instrument",
  display: "swap",
});
const geist = JetBrains_Mono({
  subsets: ["latin"],
  weight: ["400", "500"],
  variable: "--font-geist",
  display: "swap",
});

export const metadata: Metadata = {
  metadataBase: new URL("https://cleanlines.studio"),
  title: "Cleanlines Studio — Premium Content für lokale Betriebe",
  description:
    "Hochwertige Reels, KI-Visuals, Captions, Google-Beiträge und Content-Systeme für lokale Betriebe, die online professioneller wirken und mehr Vertrauen aufbauen wollen.",
  keywords: [
    "Content Studio",
    "Reels",
    "lokale Betriebe",
    "Social Media",
    "KI-Visuals",
    "Branding",
  ],
  openGraph: {
    title: "Cleanlines Studio — Premium Content für lokale Betriebe",
    description:
      "Dein Betrieb kann aussehen wie eine große Marke. Wir bauen den Content dafür.",
    type: "website",
    locale: "de_DE",
    siteName: "Cleanlines Studio",
  },
  twitter: {
    card: "summary_large_image",
    title: "Cleanlines Studio — Premium Content für lokale Betriebe",
    description:
      "Dein Betrieb kann aussehen wie eine große Marke. Wir bauen den Content dafür.",
  },
};

export const viewport: Viewport = {
  themeColor: "#050505",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="de"
      className={`${hanken.variable} ${dm.variable} ${instrument.variable} ${geist.variable}`}
    >
      <body className="grain font-body antialiased">
        <SmoothScroll>{children}</SmoothScroll>
      </body>
    </html>
  );
}
