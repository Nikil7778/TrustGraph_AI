/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "#2563eb",
          foreground: "#ffffff",
          dark: "#1d4ed8",
          light: "#eff6ff"
        },
        secondary: {
          DEFAULT: "#8b5cf6",
          foreground: "#ffffff",
          light: "#f5f3ff"
        },
        navy: {
          50: "#f8fafc",
          100: "#f1f5f9",
          800: "#1e293b",
          900: "#0f172a"
        },
        risk: {
          genuine: "#10b981",
          low: "#3b82f6",
          medium: "#f59e0b",
          high: "#f97316",
          scam: "#ef4444"
        }
      },
      borderRadius: {
        lg: "0.75rem",
        md: "0.5rem",
        sm: "0.25rem",
        xl: "1rem",
        '2xl': "1.5rem"
      }
    },
  },
  plugins: [],
}
