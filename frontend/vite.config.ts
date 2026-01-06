import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  plugins: [react()],
  // Configuración para kioskito.click/DriveP
  base: mode === 'production' ? '/DriveP/' : '/',
  optimizeDeps: {
    exclude: ['lucide-react'],
    include: ['react', 'react-dom', 'react-router-dom']
  },
  build: {
    // Optimizaciones para producción
    target: 'esnext',
    minify: 'terser',
    sourcemap: mode === 'development',
    terserOptions: {
      compress: {
        drop_console: mode === 'production',
        drop_debugger: mode === 'production',
        pure_funcs: mode === 'production' ? ['console.log', 'console.info'] : []
      }
    },
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'firebase': ['firebase/app', 'firebase/auth', 'firebase/storage'],
          'framer': ['framer-motion'],
          'charts': ['recharts'],
          'utils': ['axios'],
          'ui': ['lucide-react']
        },
        // Optimizar nombres de archivos para cache
        entryFileNames: 'assets/[name]-[hash].js',
        chunkFileNames: 'assets/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash].[ext]'
      }
    },
    chunkSizeWarningLimit: 1000,
    // Optimizar assets
    assetsInlineLimit: 4096, // Inline assets < 4kb
    cssCodeSplit: true
  },
  server: {
    port: 5173,
    strictPort: true,
    host: true,
    cors: true
  },
  preview: {
    port: 4173,
    strictPort: true,
    host: true
  },
  // Optimizaciones adicionales
  esbuild: {
    logOverride: { 'this-is-undefined-in-esm': 'silent' }
  }
}));
