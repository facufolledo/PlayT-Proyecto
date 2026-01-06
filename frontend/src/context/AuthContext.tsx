import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User as FirebaseUser, onAuthStateChanged } from 'firebase/auth';
import { auth } from '../config/firebase';
import { authService } from '../services/auth.service';
import { apiService, UsuarioResponse } from '../services/api';
import { logger } from '../utils/logger';
import { clientLogger } from '../utils/clientLogger';

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
  reloadUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [usuario, setUsuario] = useState<UsuarioResponse | null>(null);
  const [firebaseUser, setFirebaseUser] = useState<FirebaseUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [needsProfileCompletion, setNeedsProfileCompletion] = useState(false);

  // Escuchar cambios de estado de autenticación de Firebase
  useEffect(() => {
    let isInitialLoad = true;
    let tokenRefreshInterval: NodeJS.Timeout | null = null;

    const unsubscribe = onAuthStateChanged(auth, async (user: FirebaseUser | null) => {
      console.log('🔄 Firebase auth state changed:', user?.email || 'No user');
      setFirebaseUser(user);

      if (user) {
        try {
          // Usuario autenticado en Firebase, intentar obtener del backend
          const firebaseToken = await user.getIdToken();

          // Guardar token en localStorage para persistencia
          localStorage.setItem('firebase_token', firebaseToken);
          localStorage.setItem('firebase_user_email', user.email || '');

          const usuarioBackend = await apiService.firebaseAuth(firebaseToken);
          setUsuario(usuarioBackend);
          setNeedsProfileCompletion(false);
          localStorage.removeItem('needsProfileCompletion');
          console.log('✅ Usuario autenticado:', usuarioBackend.email);

          // Configurar renovación automática del token cada 50 minutos
          // (Firebase tokens expiran en 1 hora)
          if (tokenRefreshInterval) {
            clearInterval(tokenRefreshInterval);
          }

          tokenRefreshInterval = setInterval(async () => {
            try {
              const currentUser = auth.currentUser;
              if (currentUser) {
                const newToken = await currentUser.getIdToken(true);
                localStorage.setItem('firebase_token', newToken);
              }
            } catch (error) {
              // Silenciar error
            }
          }, 50 * 60 * 1000); // 50 minutos

          // Si es la carga inicial y viene de un redirect, no hacer nada
          // El componente Login/Register manejará la navegación
          if (!isInitialLoad) {
            // Solo navegar automáticamente si no es la carga inicial
            console.log('✅ Sesión restaurada automáticamente');
          }
        } catch (error: any) {
          console.log('⚠️ Usuario en Firebase pero no en backend');
          if (error.response?.status === 404) {
            setNeedsProfileCompletion(true);
            localStorage.setItem('needsProfileCompletion', 'true');
            console.log('📝 Necesita completar perfil');
          }
        }
      } else {
        // No hay usuario autenticado
        setUsuario(null);
        setNeedsProfileCompletion(false);
        localStorage.removeItem('access_token');
        localStorage.removeItem('usuario');
        localStorage.removeItem('needsProfileCompletion');
        localStorage.removeItem('firebase_token');
        localStorage.removeItem('firebase_user_email');

        // Limpiar intervalo de renovación
        if (tokenRefreshInterval) {
          clearInterval(tokenRefreshInterval);
          tokenRefreshInterval = null;
        }
      }

      setIsLoading(false);
      isInitialLoad = false;
    });

    return () => {
      unsubscribe();
      if (tokenRefreshInterval) {
        clearInterval(tokenRefreshInterval);
      }
    };
  }, []);

  // Guardar usuario en localStorage cuando cambie
  useEffect(() => {
    if (usuario) {
      localStorage.setItem('usuario', JSON.stringify(usuario));
    } else {
      localStorage.removeItem('usuario');
    }
  }, [usuario]);

  // Renovar token cuando el usuario vuelve a la pestaña (con debounce)
  useEffect(() => {
    let lastRefresh = 0;
    const REFRESH_COOLDOWN = 60000; // 1 minuto mínimo entre refreshes

    const handleVisibilityChange = async () => {
      if (document.visibilityState === 'visible' && firebaseUser) {
        const now = Date.now();
        // Solo renovar si pasó más de 1 minuto desde la última renovación
        if (now - lastRefresh < REFRESH_COOLDOWN) {
          return;
        }
        try {
          lastRefresh = now;
          const newToken = await firebaseUser.getIdToken(true);
          localStorage.setItem('firebase_token', newToken);
        } catch (error) {
          // Silenciar error, no es crítico
        }
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [firebaseUser]);

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    clientLogger.userAction('Login attempt', { email });
    try {
      // Login con Firebase (email/password)
      const user = await authService.loginWithEmail(email, password);
      setFirebaseUser(user);
      console.log('🔥 Firebase user:', user.email);
      clientLogger.info('Firebase login successful', { email: user.email });

      // Recargar el usuario para obtener el estado actualizado de emailVerified
      await user.reload();
      
      // Verificar que el email esté verificado
      if (!user.emailVerified) {
        setNeedsProfileCompletion(true);
        localStorage.setItem('needsProfileCompletion', 'true');
        clientLogger.warn('Email not verified', { email: user.email });
        throw new Error('Debes verificar tu correo electrónico antes de continuar. Revisa tu bandeja de entrada.');
      }

      // Obtener token de Firebase (forzar refresh para obtener claims actualizados)
      const firebaseToken = await user.getIdToken(true);
      console.log('🔑 Firebase token obtenido (refreshed)');

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

      // Guardar token inmediatamente
      localStorage.setItem('firebase_token', firebaseToken);
      localStorage.setItem('firebase_user_email', user.email || '');

      // Terminar loading inmediatamente para no bloquear UI
      setIsLoading(false);

      // Autenticar con backend en segundo plano (no bloquear)
      apiService.firebaseAuth(firebaseToken)
        .then(usuarioBackend => {
          setUsuario(usuarioBackend);
          setNeedsProfileCompletion(false);
          localStorage.removeItem('needsProfileCompletion');
          console.log('✅ Usuario backend encontrado:', usuarioBackend.email);
          logger.log('Login con Google exitoso:', usuarioBackend.email);
        })
        .catch(backendError => {
          console.log('❌ Error backend:', backendError);
          console.log('Status:', backendError.response?.status);
          
          // Si el usuario no existe en el backend (404), necesita completar perfil
          if (backendError.response?.status === 404) {
            console.log('📝 Usuario no encontrado, marcando needsProfileCompletion');
            setNeedsProfileCompletion(true);
            localStorage.setItem('needsProfileCompletion', 'true');
            logger.log('Usuario no encontrado en backend, necesita completar perfil');
          }
        });
    } catch (error: any) {
      console.log('💥 Error general:', error);
      logger.error('Error en login con Google:', error);
      setIsLoading(false);
      throw new Error(error.message || 'Error al iniciar sesión con Google');
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
    clientLogger.userAction('Logout attempt');
    try {
      await authService.logout();
      setUsuario(null);
      setFirebaseUser(null);
      setNeedsProfileCompletion(false); // Limpiar estado de perfil incompleto
      localStorage.removeItem('access_token');
      localStorage.removeItem('usuario');
      localStorage.removeItem('needsProfileCompletion'); // Limpiar flag de perfil
      localStorage.removeItem('firebase_token'); // Limpiar token de Firebase
      localStorage.removeItem('firebase_user_email'); // Limpiar email
      clientLogger.info('Logout successful');
    } catch (error: any) {
      logger.error('Error en logout:', error);
      clientLogger.error('Logout failed', { error: error.message });
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

  const reloadUser = async () => {
    try {
      if (firebaseUser) {
        const firebaseToken = await firebaseUser.getIdToken();
        const usuarioBackend = await apiService.firebaseAuth(firebaseToken);
        setUsuario(usuarioBackend);
        console.log('✅ Usuario recargado:', usuarioBackend.rating);
      }
    } catch (error) {
      console.error('Error al recargar usuario:', error);
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
        reloadUser,
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
