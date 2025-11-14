/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        background: '#1A1F2E',     // Fondo principal - mucho más claro
        primary: '#0055FF',        // Azul eléctrico
        secondary: '#FF006E',      // Rosa/magenta vibrante
        accent: '#FFD60A',         // Amarillo energético
        textPrimary: '#F5F5F5',    // Blanco más brillante
        textSecondary: '#94A3B8',  // Gris más claro
        cardBg: '#242B3D',         // Fondo de tarjetas - más claro
        cardBorder: '#3A4558',     // Borde más visible
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      backgroundImage: {
        'gradient-dark': 'linear-gradient(135deg, #0A0C10 0%, #111418 100%)',
      },
    },
  },
  plugins: [],
};
