/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        mono: ['JetBrains Mono', 'monospace'],
      },
      colors: {
        background: {
          dark: '#1a1a1a',
          light: '#fafaf9'
        },
        surface: {
          dark: '#242424',
          light: '#f5f5f4'
        },
        text: {
          dark: '#fafaf9',
          light: '#1a1a1a'
        },
        muted: {
          dark: '#a1a1aa',
          light: '#71717a'
        },
        sage: {
          50: '#f6f7f5',
          100: '#e3e7df',
          200: '#c8d1c0',
          300: '#a8b5a0',
          400: '#8a9a80',
          500: '#6b7d62',
          600: '#54634d',
          700: '#434f3e',
          800: '#384135',
          900: '#2f362d'
        }
      }
    },
  },
  plugins: [],
}
