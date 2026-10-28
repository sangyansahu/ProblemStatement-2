/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        canvas: '#F4F3EE',
        surface: '#FFFEFA',
        'text-primary': '#202A2D',
        'text-secondary': '#475551',
        border: '#DCDED8',
        'border-strong': '#C8CEC6',
        sidebar: '#203431',
        'nav-muted': '#A9B8B1',
        primary: {
          DEFAULT: '#2B665B',
          hover: '#1F5148',
          soft: '#E1EEEA',
        },
        bronze: '#D8A36C',
        critical: {
          DEFAULT: '#A84231',
          bg: '#F7E9E5',
        },
        caution: {
          DEFAULT: '#8C6319',
          bg: '#F5EFDF',
        },
        success: {
          DEFAULT: '#2D6B4D',
          bg: '#E4EFE7',
        },
        'search-bg': '#FAF9F5',
        'table-header': '#F8F8F3',
        progress: '#548478',
      },
      fontFamily: {
        sans: ['"DM Sans"', 'system-ui', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'monospace'],
      },
      boxShadow: {
        'subtle': '0 1px 2px 0 rgba(0, 0, 0, 0.04)',
        'panel': '0 1px 3px 0 rgba(32, 42, 45, 0.06), 0 1px 2px 0 rgba(32, 42, 45, 0.03)',
      }
    },
  },
  plugins: [],
}
