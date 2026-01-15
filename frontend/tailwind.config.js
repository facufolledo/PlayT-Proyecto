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
      animation: {
        'slide-up': 'slideUp 0.3s ease-out',
        'fade-in': 'fadeIn 0.2s ease-out',
      },
      keyframes: {
        slideUp: {
          '0%': { transform: 'translateY(100%)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
      },
    },
  },
  plugins: [],
};
