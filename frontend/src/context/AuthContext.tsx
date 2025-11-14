import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { Usuario } from '../utils/types';
import { logger } from '../utils/logger';

interface AuthContextType {
  usuario: Usuario | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (nombre: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  updateProfile: (data: Partial<Usuario>) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [usuario, setUsuario] = useState<Usuario | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Cargar usuario desde localStorage al iniciar
  useEffect(() => {
    const usuarioGuardado = localStorage.getItem('usuario');
    if (usuarioGuardado) {
      try {
        setUsuario(JSON.parse(usuarioGuardado));
      } catch (error) {
        logger.error('Error al cargar usuario:', error);
        localStorage.removeItem('usuario');
      }
    }
    setIsLoading(false);
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

  const logout = () => {
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
