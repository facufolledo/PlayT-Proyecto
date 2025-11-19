import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User as FirebaseUser } from 'firebase/auth';
import { authService } from '../services/auth.service';
import { apiService, UsuarioResponse } from '../services/api';
import { logger } from '../utils/logger';

interface AuthContextType {
  usuario: UsuarioResponse | null;
  firebaseUser: FirebaseUser | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  loginWithGoogle: () => Promise<void>;
  register: (nombre: string, email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  updateProfile: (data: Partial<UsuarioResponse>) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [usuario, setUsuario] = useState<UsuarioResponse | null>(null);
  const [firebaseUser, setFirebaseUser] = useState<FirebaseUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Cargar usuario desde localStorage al iniciar
  useEffect(() => {
    const loadUser = async () => {
      try {
        // Verificar si hay token de acceso
        const token = localStorage.getItem('access_token');
        if (token) {
          // Intentar obtener información del usuario
          const usuarioBackend = await apiService.getMe();
          setUsuario(usuarioBackend);
        }

        // Verificar si hay usuario de Firebase
        const currentFirebaseUser = authService.getCurrentFirebaseUser();
        setFirebaseUser(currentFirebaseUser);
      } catch (error) {
        logger.error('Error al cargar usuario:', error);
        localStorage.removeItem('access_token');
        localStorage.removeItem('usuario');
      } finally {
        setIsLoading(false);
      }
    };

    loadUser();
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
      // Login con el backend
      const tokenResponse = await apiService.login(email, password);
      
      // Guardar token
      localStorage.setItem('access_token', tokenResponse.access_token);
      
      // Obtener información del usuario desde el backend
      const usuarioBackend = await apiService.getMe();
      
      // Guardar usuario
      setUsuario(usuarioBackend);
      
      logger.log('Login exitoso:', usuarioBackend.email);
    } catch (error: any) {
      logger.error('Error en login:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Credenciales inválidas';
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const loginWithGoogle = async () => {
    setIsLoading(true);
    try {
      const user = await authService.loginWithGoogle();
      setFirebaseUser(user);
      
      // Obtener token de Firebase
      const firebaseToken = await user.getIdToken();
      
      // Autenticar con el backend usando el token de Firebase
      const usuarioBackend = await apiService.firebaseAuth(firebaseToken);
      setUsuario(usuarioBackend);
      
      logger.log('Login con Google exitoso:', usuarioBackend.email);
    } catch (error: any) {
      logger.error('Error en login con Google:', error);
      throw new Error(error.message || 'Error al iniciar sesión con Google');
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (nombre: string, email: string, password: string) => {
    setIsLoading(true);
    try {
      // Registro con Firebase
      const user = await authService.registerWithEmail(email, password);
      setFirebaseUser(user);
      
      logger.log('Registro exitoso, redirigir a completar perfil');
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

  const isAuthenticated = !!usuario || !!localStorage.getItem('access_token');

  return (
    <AuthContext.Provider
      value={{
        usuario,
        firebaseUser,
        isAuthenticated,
        isLoading,
        login,
        loginWithGoogle,
        register,
        logout,
        updateProfile,
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
