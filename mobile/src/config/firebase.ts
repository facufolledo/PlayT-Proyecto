// Configuración de Firebase
import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import Constants from 'expo-constants';

const firebaseConfig = {
  apiKey: Constants.expoConfig?.extra?.firebaseApiKey || 'demo-key',
  authDomain: Constants.expoConfig?.extra?.firebaseAuthDomain || 'demo.firebaseapp.com',
  projectId: Constants.expoConfig?.extra?.firebaseProjectId || 'demo-project',
  storageBucket: Constants.expoConfig?.extra?.firebaseStorageBucket || 'demo.appspot.com',
  messagingSenderId: Constants.expoConfig?.extra?.firebaseMessagingSenderId || '123456789',
  appId: Constants.expoConfig?.extra?.firebaseAppId || '1:123456789:web:xxxxx',
};

// Inicializar Firebase
const app = initializeApp(firebaseConfig);

// Inicializar Auth
export const auth = getAuth(app);

export default app;
