// Configuración de Firebase
// IMPORTANTE: Reemplazar con tus credenciales reales de Firebase Console
import { initializeApp } from 'firebase/app';
import { getAuth, GoogleAuthProvider } from 'firebase/auth';

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY || "tu-api-key",
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || "tu-proyecto.firebaseapp.com",
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID || "tu-proyecto-id",
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || "tu-proyecto.appspot.com",
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || "123456789",
  appId: import.meta.env.VITE_FIREBASE_APP_ID || "tu-app-id"
};

// Inicializar Firebase
const app = initializeApp(firebaseConfig);

// Inicializar Auth
export const auth = getAuth(app);

// Provider de Google
export const googleProvider = new GoogleAuthProvider();

export default app;
