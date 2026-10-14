module.exports = {
  content: ['./index.html'],
  theme: {
    extend: {
      fontFamily: { sans: ['-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', '"Noto Sans TC"', 'sans-serif'] },
      colors: { primary: { 50: '#fff7ed', 100: '#ffedd5', 500: '#f97316', 600: '#ea580c', 700: '#c2410c', 800: '#9a3412' } },
      boxShadow: { glow: '0 0 20px rgba(234, 88, 12, 0.15)' }
    }
  },
  plugins: []
};
