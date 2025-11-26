import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.tsx';
import './index.css';
import { registerServiceWorker, setupInstallPrompt } from './utils/pwa';

// Registrar Service Worker y configurar PWA
if (import.meta.env.PROD) {
  registerServiceWorker();
  setupInstallPrompt();
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>
);
