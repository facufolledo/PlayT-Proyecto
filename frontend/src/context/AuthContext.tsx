import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { signInWithPopup, signOut as firebaseSignOut } from 'firebase/auth';
import { auth, googleProvider } from '../config/firebase';
import { Usuario } from '../utils/types';
import { logger } from '../utils/logger';

interface AuthContextType {
  usuario: Usuario | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  loginWithGoogle: () => Promise<void>;
  register: (nombre: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  updateProfile: (data: Partial<Usuario>) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [usuario, setUsuario] = useState<Usuario | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Escuchar cambios en el estado de autenticación de Firebase
  useEffect(() => {
    const unsubscribe = auth.onAuthStateChanged((firebaseUser) => {
      if (firebaseUser) {
        // Usuario autenticado en Firebase
        const usuarioGuardado = localStorage.getItem('usuario');
        if (usuarioGuardado) {
          try {
            setUsuario(JSON.parse(usuarioGuardado));
          } catch (error) {
            logger.error('Error al cargar usuario:', error);
            // Si hay error, crear usuario desde Firebase
            const nuevoUsuario: Usuario = {
              id: firebaseUser.uid,
              nombre: firebaseUser.displayName || firebaseUser.email?.split('@')[0] || 'Usuario',
              email: firebaseUser.email || '',
              avatar: firebaseUser.photoURL || undefined,
              rol: 'jugador',
              estadisticas: {
                partidosJugados: 0,
                partidosGanados: 0,
                torneosParticipados: 0,
                torneosGanados: 0,
              },
              createdAt: new Date().toISOString(),
            };
            setUsuario(nuevoUsuario);
          }
        } else {
          // No hay usuario guardado, crear desde Firebase
          const nuevoUsuario: Usuario = {
            id: firebaseUser.uid,
            nombre: firebaseUser.displayName || firebaseUser.email?.split('@')[0] || 'Usuario',
            email: firebaseUser.email || '',
            avatar: firebaseUser.photoURL || undefined,
            rol: 'jugador',
            estadisticas: {
              partidosJugados: 0,
              partidosGanados: 0,
              torneosParticipados: 0,
              torneosGanados: 0,
            },
            createdAt: new Date().toISOString(),
          };
          setUsuario(nuevoUsuario);
        }
      } else {
        // No hay usuario autenticado
        setUsuario(null);
        localStorage.removeItem('usuario');
      }
      setIsLoading(false);
    });

    // Cleanup: desuscribirse cuando el componente se desmonte
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
      // TODO: Reemplazar con llamada real al backend
      // Simulación de login
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Usuario de prueba
      const usuarioMock: Usuario = {
        id: crypto.randomUUID(),
        nombre: email.split('@')[0],
        email,
        rol: 'jugador',
        estadisticas: {
          partidosJugados: 0,
          partidosGanados: 0,
          torneosParticipados: 0,
          torneosGanados: 0,
        },
        createdAt: new Date().toISOString(),
      };

      setUsuario(usuarioMock);
    } catch (error) {
      logger.error('Error en login:', error);
      throw new Error('Credenciales inválidas');
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (nombre: string, email: string, password: string) => {
    setIsLoading(true);
    try {
      // TODO: Reemplazar con llamada real al backend
      // Simulación de registro
      await new Promise(resolve => setTimeout(resolve, 1000));

      const nuevoUsuario: Usuario = {
        id: crypto.randomUUID(),
        nombre,
        email,
        rol: 'jugador',
        estadisticas: {
          partidosJugados: 0,
          partidosGanados: 0,
          torneosParticipados: 0,
          torneosGanados: 0,
        },
        createdAt: new Date().toISOString(),
      };

      setUsuario(nuevoUsuario);
    } catch (error) {
      logger.error('Error en registro:', error);
      throw new Error('Error al registrar usuario');
    } finally {
      setIsLoading(false);
    }
  };

  const loginWithGoogle = async () => {
    setIsLoading(true);
    try {
      const result = await signInWithPopup(auth, googleProvider);
      const user = result.user;

      // Crear usuario con datos de Google
      const nuevoUsuario: Usuario = {
        id: user.uid,
        nombre: user.displayName || user.email?.split('@')[0] || 'Usuario',
        email: user.email || '',
        avatar: user.photoURL || undefined,
        rol: 'jugador',
        estadisticas: {
          partidosJugados: 0,
          partidosGanados: 0,
          torneosParticipados: 0,
          torneosGanados: 0,
        },
        createdAt: new Date().toISOString(),
      };

      setUsuario(nuevoUsuario);
      logger.log('Login con Google exitoso:', user.email);
    } catch (error: any) {
      logger.error('Error en login con Google:', error);
      if (error.code === 'auth/popup-closed-by-user') {
        throw new Error('Inicio de sesión cancelado');
      }
      throw new Error('Error al iniciar sesión con Google');
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      await firebaseSignOut(auth);
    } catch (error) {
      logger.error('Error al cerrar sesión:', error);
    }
    setUsuario(null);
    localStorage.removeItem('usuario');
  };

  const updateProfile = (data: Partial<Usuario>) => {
    if (usuario) {
      setUsuario({ ...usuario, ...data });
    }
  };

  return (
    <AuthContext.Provider
      value={{
        usuario,
        isAuthenticated: !!usuario,
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
