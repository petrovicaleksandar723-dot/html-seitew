import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: "#050505",
        "bg-2": "#0a0908",
        surface: "#0f0e0c",
        ink: "#f4f0e8",
        dim: "#a8a39a",
        muted: "#6e6a62",
        gold: "#d8b274",
        "gold-bright": "#f0d49a",
        "gold-deep": "#a87f3e",
        line: "rgba(255,255,255,0.08)",
      },
      fontFamily: {
        display: ["var(--font-hanken)", "system-ui", "sans-serif"],
        body: ["var(--font-dm)", "system-ui", "sans-serif"],
        serif: ["var(--font-instrument)", "Georgia", "serif"],
        mono: ["var(--font-geist)", "ui-monospace", "monospace"],
      },
      maxWidth: {
        shell: "1680px",
        content: "1240px",
      },
      transitionTimingFunction: {
        "out-expo": "cubic-bezier(0.22, 1, 0.36, 1)",
        spring: "cubic-bezier(0.34, 1.56, 0.64, 1)",
      },
    },
  },
  plugins: [],
};

export default config;
