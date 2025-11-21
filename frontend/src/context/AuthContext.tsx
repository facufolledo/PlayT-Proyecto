import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User as FirebaseUser, onAuthStateChanged } from 'firebase/auth';
import { auth } from '../config/firebase';
import { authService } from '../services/auth.service';
import { apiService, UsuarioResponse } from '../services/api';
import { logger } from '../utils/logger';

interface AuthContextType {
  usuario: UsuarioResponse | null;
  firebaseUser: FirebaseUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  needsProfileCompletion: boolean;
  login: (email: string, password: string) => Promise<void>;
  loginWithGoogle: () => Promise<void>;
  register: (nombre: string, email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  updateProfile: (data: Partial<UsuarioResponse>) => void;
  completeProfile: (datos: any) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [usuario, setUsuario] = useState<UsuarioResponse | null>(null);
  const [firebaseUser, setFirebaseUser] = useState<FirebaseUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [needsProfileCompletion, setNeedsProfileCompletion] = useState(false);

  // Escuchar cambios de estado de autenticación de Firebase
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (user: FirebaseUser | null) => {
      console.log('🔄 Firebase auth state changed:', user?.email || 'No user');
      setFirebaseUser(user);
      
      if (user) {
        try {
          // Usuario autenticado en Firebase, intentar obtener del backend
          const firebaseToken = await user.getIdToken();
          const usuarioBackend = await apiService.firebaseAuth(firebaseToken);
          setUsuario(usuarioBackend);
          setNeedsProfileCompletion(false);
          localStorage.removeItem('needsProfileCompletion');
          console.log('✅ Sesión restaurada:', usuarioBackend.email);
        } catch (error: any) {
          console.log('⚠️ Usuario en Firebase pero no en backend');
          if (error.response?.status === 404) {
            setNeedsProfileCompletion(true);
            localStorage.setItem('needsProfileCompletion', 'true');
          }
        }
      } else {
        // No hay usuario autenticado
        setUsuario(null);
        setNeedsProfileCompletion(false);
        localStorage.removeItem('access_token');
        localStorage.removeItem('usuario');
        localStorage.removeItem('needsProfileCompletion');
      }
      
      setIsLoading(false);
    });

    return () => unsubscribe();
  }, []);

  // Guardar usuario en localStorage cuando cambie
  useEffect(() => {
    if (usuario) {
      localStorage.setItem('usuario', JSON.stringify(usuario));
    } else {
      localStorage.removeItem('usuario');
    }
  }, [usuario]);

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      // Login con Firebase (email/password)
      const user = await authService.loginWithEmail(email, password);
      setFirebaseUser(user);
      console.log('🔥 Firebase user:', user.email);
      
      // Verificar que el email esté verificado
      if (!user.emailVerified) {
        setNeedsProfileCompletion(true);
        localStorage.setItem('needsProfileCompletion', 'true');
        throw new Error('Debes verificar tu correo electrónico antes de continuar. Revisa tu bandeja de entrada.');
      }
      
      // Obtener token de Firebase
      const firebaseToken = await user.getIdToken();
      console.log('🔑 Firebase token obtenido');
      
      try {
        // Intentar autenticar con el backend usando el token de Firebase
        const usuarioBackend = await apiService.firebaseAuth(firebaseToken);
        setUsuario(usuarioBackend);
        setNeedsProfileCompletion(false);
        localStorage.removeItem('needsProfileCompletion');
        console.log('✅ Usuario backend encontrado:', usuarioBackend.email);
        logger.log('Login exitoso:', usuarioBackend.email);
      } catch (backendError: any) {
        console.log('❌ Error backend:', backendError);
        console.log('Status:', backendError.response?.status);
        // Si el usuario no existe en el backend (404), necesita completar perfil
        if (backendError.response?.status === 404) {
          console.log('📝 Usuario no encontrado, marcando needsProfileCompletion');
          setNeedsProfileCompletion(true);
          localStorage.setItem('needsProfileCompletion', 'true');
          logger.log('Usuario no encontrado en backend, necesita completar perfil');
          // No lanzar error, el Login.tsx manejará la redirección
          return;
        }
        // Si es otro error, lanzarlo
        throw backendError;
      }
    } catch (error: any) {
      console.log('💥 Error general:', error);
      logger.error('Error en login:', error);
      throw new Error(error.message || 'Error al iniciar sesión');
    } finally {
      setIsLoading(false);
    }
  };

  const loginWithGoogle = async () => {
    setIsLoading(true);
    try {
      const user = await authService.loginWithGoogle();
      setFirebaseUser(user);
      console.log('🔥 Firebase user:', user.email);
      
      // Obtener token de Firebase
      const firebaseToken = await user.getIdToken();
      console.log('🔑 Firebase token obtenido');
      
      try {
        // Intentar autenticar con el backend usando el token de Firebase
        const usuarioBackend = await apiService.firebaseAuth(firebaseToken);
        setUsuario(usuarioBackend);
        console.log('✅ Usuario backend encontrado:', usuarioBackend.email);
        logger.log('Login con Google exitoso:', usuarioBackend.email);
      } catch (backendError: any) {
        console.log('❌ Error backend:', backendError);
        console.log('Status:', backendError.response?.status);
        // Si el usuario no existe en el backend (404), necesita completar perfil
        if (backendError.response?.status === 404) {
          console.log('📝 Usuario no encontrado, marcando needsProfileCompletion');
          setNeedsProfileCompletion(true);
          localStorage.setItem('needsProfileCompletion', 'true');
          logger.log('Usuario no encontrado en backend, necesita completar perfil');
          // No lanzar error, el Login.tsx manejará la redirección
          return;
        }
        // Si es otro error, lanzarlo
        throw backendError;
      }
    } catch (error: any) {
      console.log('💥 Error general:', error);
      logger.error('Error en login con Google:', error);
      throw new Error(error.message || 'Error al iniciar sesión con Google');
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (nombre: string, email: string, password: string) => {
    setIsLoading(true);
    try {
      // Registro con Firebase (email/password)
      const user = await authService.registerWithEmail(email, password);
      setFirebaseUser(user);
      
      // No marcar needsProfileCompletion todavía
      // El usuario debe verificar su email primero
      
      logger.log('Registro con Firebase exitoso, debe verificar email');
    } catch (error: any) {
      logger.error('Error en registro:', error);
      throw new Error(error.message || 'Error al registrar usuario');
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    setIsLoading(true);
    try {
      await authService.logout();
      setUsuario(null);
      setFirebaseUser(null);
      localStorage.removeItem('access_token');
      localStorage.removeItem('usuario');
    } catch (error: any) {
      logger.error('Error en logout:', error);
      throw new Error(error.message || 'Error al cerrar sesión');
    } finally {
      setIsLoading(false);
    }
  };

  const updateProfile = (data: Partial<UsuarioResponse>) => {
    if (usuario) {
      setUsuario({ ...usuario, ...data });
    }
  };

  const completeProfile = async (datos: any) => {
    try {
      const usuarioCreado = await authService.completarPerfil(datos);
      setUsuario(usuarioCreado);
      setNeedsProfileCompletion(false);
      localStorage.removeItem('needsProfileCompletion');
      logger.log('Perfil completado y usuario actualizado en contexto');
    } catch (error: any) {
      logger.error('Error al completar perfil:', error);
      throw error;
    }
  };

  // Usuario está autenticado si tiene firebaseUser O usuario del backend
  const isAuthenticated = !!firebaseUser || !!usuario;

  return (
    <AuthContext.Provider
      value={{
        usuario,
        firebaseUser,
        isAuthenticated,
        isLoading,
        needsProfileCompletion,
        login,
        loginWithGoogle,
        register,
        logout,
        updateProfile,
        completeProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth debe usarse dentro de AuthProvider');
  }
  return context;
}
