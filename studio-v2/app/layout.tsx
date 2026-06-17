import type { Metadata, Viewport } from "next";
import {
  Hanken_Grotesk,
  DM_Sans,
  Instrument_Serif,
  JetBrains_Mono,
} from "next/font/google";
import "./globals.css";
import { SmoothScroll } from "@/components/smooth-scroll";
import { Nav } from "@/components/nav";

const display = Hanken_Grotesk({
  subsets: ["latin"],
  weight: ["400", "500", "700", "800"],
  variable: "--font-display",
});
const body = DM_Sans({
  subsets: ["latin"],
  weight: ["400", "500"],
  variable: "--font-body",
});
const serif = Instrument_Serif({
  subsets: ["latin"],
  weight: ["400"],
  style: ["italic", "normal"],
  variable: "--font-serif",
});
const mono = JetBrains_Mono({
  subsets: ["latin"],
  weight: ["400", "500"],
  variable: "--font-mono",
});

export const metadata: Metadata = {
  title: "Clean Lines Studios — Content, der deinen Betrieb sichtbar macht",
  description:
    "Premium Content-Produktion für lokale Betriebe: Reels, Fotografie und ein Auftritt, der so hochwertig wirkt wie deine Arbeit. Clean Lines Studios.",
  openGraph: {
    title: "Clean Lines Studios",
    description:
      "Premium Content-Produktion für lokale Betriebe — Reels, Fotografie, sichtbares Wachstum.",
    type: "website",
  },
};

export const viewport: Viewport = {
  themeColor: "#060504",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html
      lang="de"
      className={`${display.variable} ${body.variable} ${serif.variable} ${mono.variable}`}
    >
      <body className="bg-bg font-body text-ink antialiased">
        <div className="grain" aria-hidden />
        <Nav />
        <SmoothScroll>{children}</SmoothScroll>
      </body>
    </html>
  );
}
