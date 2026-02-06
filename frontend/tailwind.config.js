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
        // Custom brand colors matching the Django theme
        primary: {
          50: '#f5f3ff',
          100: '#ede9fe',
          200: '#ddd6fe',
          300: '#c4b5fd',
          400: '#a78bfa',
          500: '#8b5cf6',
          600: '#7c3aed',
          700: '#6d28d9',
          800: '#5b21b6',
          900: '#4c1d95',
          950: '#2e1065',
        },
        accent: {
          green: '#22c55e',
          cyan: '#06b6d4',
          pink: '#ec4899',
          amber: '#f59e0b',
          red: '#ef4444',
        },
        dark: {
          bg: '#0f0f0f',
          card: '#1a1a1a',
          border: '#333333',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Menlo', 'monospace'],
      },
      // Session 943: Unified typography for dark theme
      typography: {
        DEFAULT: {
          css: {
            maxWidth: 'none',
          },
        },
        // Custom dark theme prose - used with prose-dark class
        dark: {
          css: {
            '--tw-prose-body': '#e5e5e5',           // gray-200
            '--tw-prose-headings': '#ffffff',
            '--tw-prose-lead': '#d4d4d4',           // gray-300
            '--tw-prose-links': '#a78bfa',          // primary-400
            '--tw-prose-bold': '#ffffff',
            '--tw-prose-counters': '#a78bfa',       // primary-400
            '--tw-prose-bullets': '#a78bfa',        // primary-400
            '--tw-prose-hr': '#404040',             // gray-700
            '--tw-prose-quotes': '#d4d4d4',         // gray-300
            '--tw-prose-quote-borders': '#7c3aed',  // primary-600
            '--tw-prose-captions': '#a3a3a3',       // gray-400
            '--tw-prose-code': '#c4b5fd',           // primary-300
            '--tw-prose-pre-code': '#e5e5e5',       // gray-200
            '--tw-prose-pre-bg': '#171717',         // gray-900
            '--tw-prose-th-borders': '#525252',     // gray-600
            '--tw-prose-td-borders': '#404040',     // gray-700
            // Additional customizations
            'code': {
              backgroundColor: '#262626',           // gray-800
              padding: '0.25rem 0.375rem',
              borderRadius: '0.375rem',
              fontWeight: '400',
            },
            'code::before': {
              content: '""',
            },
            'code::after': {
              content: '""',
            },
            'pre': {
              backgroundColor: '#171717',           // gray-900
              border: '1px solid #404040',          // gray-700
              borderRadius: '0.5rem',
            },
            'a': {
              textDecoration: 'underline',
              textUnderlineOffset: '2px',
              '&:hover': {
                color: '#c4b5fd',                   // primary-300
              },
            },
            'blockquote': {
              borderLeftColor: '#7c3aed',           // primary-600
              fontStyle: 'normal',
            },
            'h1, h2, h3, h4': {
              fontWeight: '600',
            },
            'table': {
              fontSize: '0.875rem',
            },
            'thead th': {
              color: '#d4d4d4',                     // gray-300
              fontWeight: '500',
            },
            'tbody tr': {
              borderBottomColor: '#404040',         // gray-700
            },
          },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
