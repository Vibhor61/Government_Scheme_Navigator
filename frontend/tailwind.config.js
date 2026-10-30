/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        forest: {
          50: '#F2F8F5',
          100: '#E8F3EE',
          200: '#C7E2D5',
          300: '#9BCCB5',
          400: '#5BAE89',
          500: '#2F916B',
          600: '#176B52', // Core Brand Primary
          700: '#135843',
          800: '#0F4534',
          900: '#0B3327',
          950: '#051C15',
        },
        sand: {
          50: '#FAFAF7', // Core Background Warm Off-white
          100: '#F5F5F0',
          200: '#EBEBE3',
          300: '#DDDCD3',
        },
        charcoal: {
          50: '#F6F7F6',
          100: '#EBEEEB',
          200: '#D5DAD6',
          400: '#8A978E',
          500: '#5C6D63', // Secondary Muted Grey-Green Text
          700: '#344038',
          800: '#27312B',
          900: '#202923', // Core Primary Text
          950: '#141A16',
        },
        border: {
          subtle: '#E3E7E4',
          DEFAULT: '#E3E7E4',
          strong: '#D0D6D2',
        },
        saffron: {
          500: '#E06D14', // Subtle Saffron Accent
          600: '#C85A09',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
      fontSize: {
        xs: ['0.875rem', { lineHeight: '1.25rem' }],
        sm: ['1rem', { lineHeight: '1.5rem' }],
      },
      boxShadow: {
        'subtle': '0 1px 2px 0 rgba(32, 41, 35, 0.04)',
        'card': '0 1px 3px 0 rgba(32, 41, 35, 0.06), 0 1px 2px -1px rgba(32, 41, 35, 0.06)',
        'elevated': '0 4px 6px -1px rgba(32, 41, 35, 0.06), 0 2px 4px -2px rgba(32, 41, 35, 0.04)',
      }
    },
  },
  plugins: [],
}
