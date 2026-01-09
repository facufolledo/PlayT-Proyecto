// Servicio de autenticación con Firebase
import { 
  signInWithPopup,
  signInWithRedirect,
  getRedirectResult,
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

// Detectar si es móvil
const isMobile = () => {
  return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ||
         window.innerWidth < 768;
};

class AuthService {
  // Login con Google - usar popup en desktop, redirect en móvil
  async loginWithGoogle(): Promise<User> {
    try {
      if (isMobile()) {
        // En móviles usar redirect para evitar problemas COOP
        logger.log('Usando signInWithRedirect para móvil');
        await signInWithRedirect(auth, googleProvider);
        // signInWithRedirect no retorna inmediatamente, el resultado se obtiene en getRedirectResult
        throw new Error('REDIRECT_IN_PROGRESS');
      } else {
        // En desktop usar popup
        logger.log('Usando signInWithPopup para desktop');
        const result = await signInWithPopup(auth, googleProvider);
        logger.log('Login con Google exitoso:', result.user.email);
        return result.user;
      }
    } catch (error: any) {
      if (error.message === 'REDIRECT_IN_PROGRESS') {
        throw error; // Re-lanzar para que el componente sepa que está en progreso
      }
      logger.error('Error en login con Google:', error);
      
      // Errores específicos de COOP
      if (error.code === 'auth/popup-blocked' || 
          error.message.includes('Cross-Origin-Opener-Policy')) {
        logger.log('Popup bloqueado, intentando con redirect');
        await signInWithRedirect(auth, googleProvider);
        throw new Error('REDIRECT_IN_PROGRESS');
      }
      
      throw new Error(error.message || 'Error al iniciar sesión con Google');
    }
  }

  // Verificar resultado de redirect (llamar al cargar la página)
  async checkRedirectResult(): Promise<User | null> {
    try {
      const result = await getRedirectResult(auth);
      if (result?.user) {
        logger.log('Login con Google (redirect) exitoso:', result.user.email);
        return result.user;
      }
      return null;
    } catch (error: any) {
      logger.error('Error en redirect result:', error);
      throw new Error(error.message || 'Error al procesar login con Google');
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
      
      // Enviar email de verificación
      await this.sendVerificationEmail(result.user);
      
      logger.log('Registro exitoso:', result.user.email);
      return result.user;
    } catch (error: any) {
      logger.error('Error en registro:', error);
      if (error.code === 'auth/email-already-in-use') {
        throw new Error('Este email ya está registrado. Por favor, inicia sesión o recupera tu contraseña.');
      }
      if (error.code === 'auth/weak-password') {
        throw new Error('La contraseña debe tener al menos 6 caracteres');
      }
      if (error.code === 'auth/invalid-email') {
        throw new Error('Email inválido');
      }
      throw new Error(error.message || 'Error al registrar usuario');
    }
  }

  // Enviar email de verificación
  async sendVerificationEmail(user: User): Promise<void> {
    try {
      const { sendEmailVerification } = await import('firebase/auth');
      
      // Configuración opcional para personalizar el email
      const actionCodeSettings = {
        // URL a la que redirigir después de verificar - Simplificada para debug
        url: `${window.location.origin}/Drive/login?verified=true`,
        // Esto permite que el enlace se abra en la misma ventana
        handleCodeInApp: false,
      };
      
      await sendEmailVerification(user, actionCodeSettings);
      logger.log('Email de verificación enviado');
    } catch (error: any) {
      logger.error('Error al enviar email de verificación:', error);
      throw new Error('Error al enviar email de verificación');
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
  async completarPerfil(datos: PerfilCompleto): Promise<any> {
    try {
      const token = await this.getToken();
      if (!token) throw new Error('No hay sesión activa');

      const response = await fetch(`${import.meta.env.VITE_API_URL}/usuarios/completar-perfil`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(datos)
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Error al guardar el perfil');
      }

      const usuario = await response.json();
      logger.log('Perfil completado exitosamente');
      return usuario;
    } catch (error: any) {
      logger.error('Error al completar perfil:', error);
      throw new Error(error.message || 'Error al completar el perfil');
    }
  }

  // Obtener usuario actual de Firebase
  getCurrentFirebaseUser(): User | null {
    return auth.currentUser;
  }

  // Enviar email para restablecer contraseña
  async sendPasswordResetEmail(email: string): Promise<void> {
    try {
      const { sendPasswordResetEmail } = await import('firebase/auth');
      
      // Configuración opcional para personalizar el email
      const actionCodeSettings = {
        url: `${window.location.origin}/Drive/login?reset=true`,
        handleCodeInApp: false,
      };
      
      await sendPasswordResetEmail(auth, email, actionCodeSettings);
      logger.log('Email de recuperación enviado a:', email);
    } catch (error: any) {
      logger.error('Error al enviar email de recuperación:', error);
      if (error.code === 'auth/user-not-found') {
        throw new Error('No existe una cuenta con este email');
      }
      if (error.code === 'auth/invalid-email') {
        throw new Error('Email inválido');
      }
      throw new Error('Error al enviar email de recuperación');
    }
  }
}

export const authService = new AuthService();
