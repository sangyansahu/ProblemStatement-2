/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          900: '#142544',
          800: '#1F3A68', // Deep navy primary
          700: '#2A4A80',
          50: '#F4F7FB',
        },
        accent: {
          saffron: '#D97706', // Saffron restrained accent
          saffronHover: '#B45309',
        },
        govborder: '#D1D5DB',
      },
      fontFamily: {
        sans: ['Noto Sans', 'Segoe UI', 'Roboto', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
