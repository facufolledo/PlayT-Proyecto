// Servicio de autenticación con Firebase
import { 
  signInWithPopup, 
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut,
  User
} from 'firebase/auth';
import { auth, googleProvider } from '../config/firebase';
import { logger } from '../utils/logger';

export interface PerfilCompleto {
  nombre: string;
  apellido: string;
  dni: string;
  fecha_nacimiento: string;
  genero: 'masculino' | 'femenino';
  categoria_inicial: string;
  mano_habil?: 'derecha' | 'zurda';
  posicion_preferida?: 'drive' | 'reves' | 'indiferente';
  telefono?: string;
  ciudad?: string;
}

class AuthService {
  // Login con Google
  async loginWithGoogle(): Promise<User> {
    try {
      const result = await signInWithPopup(auth, googleProvider);
      logger.log('Login con Google exitoso:', result.user.email);
      return result.user;
    } catch (error: any) {
      logger.error('Error en login con Google:', error);
      throw new Error(error.message || 'Error al iniciar sesión con Google');
    }
  }

  // Login con email y contraseña
  async loginWithEmail(email: string, password: string): Promise<User> {
    try {
      const result = await signInWithEmailAndPassword(auth, email, password);
      logger.log('Login con email exitoso:', result.user.email);
      return result.user;
    } catch (error: any) {
      logger.error('Error en login con email:', error);
      throw new Error('Credenciales inválidas');
    }
  }

  // Registro con email y contraseña
  async registerWithEmail(email: string, password: string): Promise<User> {
    try {
      const result = await createUserWithEmailAndPassword(auth, email, password);
      logger.log('Registro exitoso:', result.user.email);
      return result.user;
    } catch (error: any) {
      logger.error('Error en registro:', error);
      if (error.code === 'auth/email-already-in-use') {
        throw new Error('El email ya está registrado');
      }
      throw new Error(error.message || 'Error al registrar usuario');
    }
  }

  // Logout
  async logout(): Promise<void> {
    try {
      await signOut(auth);
      logger.log('Logout exitoso');
    } catch (error: any) {
      logger.error('Error en logout:', error);
      throw new Error('Error al cerrar sesión');
    }
  }

  // Obtener token de Firebase
  async getToken(): Promise<string | null> {
    try {
      const user = auth.currentUser;
      if (!user) return null;
      return await user.getIdToken();
    } catch (error) {
      logger.error('Error al obtener token:', error);
      return null;
    }
  }

  // Verificar si el usuario completó su perfil
  async checkProfileComplete(): Promise<boolean> {
    try {
      const token = await this.getToken();
      if (!token) return false;

      // TODO: Llamar al backend para verificar si el perfil está completo
      const response = await fetch(`${import.meta.env.VITE_API_URL}/usuarios/me`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) return false;

      const data = await response.json();
      return !!data.categoria_inicial; // Si tiene categoría, el perfil está completo
    } catch (error) {
      logger.error('Error al verificar perfil:', error);
      return false;
    }
  }

  // Completar perfil del usuario
  async completarPerfil(datos: PerfilCompleto): Promise<void> {
    try {
      const token = await this.getToken();
      if (!token) throw new Error('No hay sesión activa');

      // TODO: Llamar al backend para guardar los datos
      const response = await fetch(`${import.meta.env.VITE_API_URL}/usuarios/completar-perfil`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(datos)
      });

      if (!response.ok) {
        throw new Error('Error al guardar el perfil');
      }

      logger.log('Perfil completado exitosamente');
    } catch (error: any) {
      logger.error('Error al completar perfil:', error);
      throw new Error(error.message || 'Error al completar el perfil');
    }
  }
}

export const authService = new AuthService();
