import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#060504",
        "bg-2": "#0b0a08",
        surface: "#100e0b",
        ink: "#f5f1e9",
        dim: "#aaa49a",
        muted: "#726c62",
        gold: "#d8b274",
        "gold-bright": "#f1d6a0",
        "gold-deep": "#a87f3e",
        line: "rgba(255,255,255,0.09)",
      },
      fontFamily: {
        display: ["var(--font-display)", "system-ui", "sans-serif"],
        body: ["var(--font-body)", "system-ui", "sans-serif"],
        serif: ["var(--font-serif)", "Georgia", "serif"],
        mono: ["var(--font-mono)", "ui-monospace", "monospace"],
      },
      maxWidth: {
        shell: "1680px",
        content: "1280px",
      },
      transitionTimingFunction: {
        "out-expo": "cubic-bezier(0.16, 1, 0.3, 1)",
      },
    },
  },
  plugins: [],
};

export default config;
