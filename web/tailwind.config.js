/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        // Base colors
        black: "#0a0a0a",
        charcoal: "#141414",
        slate: "#1a1a1a",

        // Gold accent (primary)
        gold: {
          DEFAULT: "#d4a853",
          dim: "#8b7235",
          bright: "#f5d485",
        },

        // Status colors
        green: {
          DEFAULT: "#2d8a4e",
          bright: "#4ade80",
        },
        red: {
          DEFAULT: "#c73434",
          dim: "#8a2424",
        },

        // Text
        text: {
          DEFAULT: "#e8e8e8",
          dim: "#6b6b6b",
          muted: "#4a4a4a",
        },

        // Borders
        border: {
          DEFAULT: "#2a2a2a",
          hover: "#3a3a3a",
        },

        // shadcn/ui compatibility
        background: "#0a0a0a",
        foreground: "#e8e8e8",
        card: {
          DEFAULT: "#141414",
          foreground: "#e8e8e8",
        },
        popover: {
          DEFAULT: "#141414",
          foreground: "#e8e8e8",
        },
        primary: {
          DEFAULT: "#d4a853",
          foreground: "#0a0a0a",
        },
        secondary: {
          DEFAULT: "#1a1a1a",
          foreground: "#e8e8e8",
        },
        muted: {
          DEFAULT: "#1a1a1a",
          foreground: "#6b6b6b",
        },
        accent: {
          DEFAULT: "#1a1a1a",
          foreground: "#e8e8e8",
        },
        destructive: {
          DEFAULT: "#c73434",
          foreground: "#e8e8e8",
        },
        ring: "#d4a853",
        input: "#2a2a2a",
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      fontFamily: {
        display: ["var(--font-bebas)", "sans-serif"],
        mono: ["var(--font-jetbrains)", "monospace"],
        serif: ["var(--font-source-serif)", "Georgia", "serif"],
      },
      keyframes: {
        "accordion-down": {
          from: { height: 0 },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: 0 },
        },
        ticker: {
          "0%": { transform: "translateX(0)" },
          "100%": { transform: "translateX(-50%)" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
        ticker: "ticker 30s linear infinite",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};
