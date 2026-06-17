import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        paper: { 0: "#f4efe4", 1: "#efe8da", 2: "#e7ddca" },
        ink: { 0: "#1a1410", soft: "rgba(26,20,16,.66)" },
        gold: { DEFAULT: "#9a6a2b", bright: "#b9893f" },
        noir: { 0: "#0c0a07", 1: "#12100a" },
      },
      fontFamily: {
        serif: ["var(--font-fraunces)", "Georgia", "serif"],
        sans: ["var(--font-hanken)", "system-ui", "sans-serif"],
      },
      maxWidth: { shell: "1720px" },
    },
  },
  // Keep the bespoke design system intact — no utility reset conflicts.
  corePlugins: { preflight: false },
  plugins: [],
};

export default config;
