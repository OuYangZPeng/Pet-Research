/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: [
          'Inter',
          'system-ui',
          '-apple-system',
          'BlinkMacSystemFont',
          'PingFang SC',
          'Hiragino Sans GB',
          'Microsoft YaHei',
          'sans-serif',
        ],
      },
      colors: {
        ink: {
          50: '#f7f8fa',
          100: '#eef1f5',
          200: '#dde2ea',
          300: '#bcc4d2',
          400: '#8a93a6',
          500: '#5e6776',
          600: '#3f4753',
          700: '#2c333d',
          800: '#1b2028',
          900: '#0f131a',
        },
        accent: {
          DEFAULT: '#0ea5a3',
          hover: '#0d8c8a',
        },
        warn: '#f59e0b',
        danger: '#ef4444',
        ok: '#10b981',
      },
      boxShadow: {
        card: '0 1px 2px rgba(15,19,26,0.04), 0 6px 16px rgba(15,19,26,0.06)',
      },
    },
  },
  plugins: [],
};
