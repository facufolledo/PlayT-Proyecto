import { Usuario, PerfilCompleto } from '../types';
import { logger } from '../utils/logger';

// MOCK: Simula Firebase Auth y backend
// Cuando el backend esté listo, reemplazar con llamadas reales
class AuthService {
  // Login con email (MOCK)
  async loginWithEmail(email: string, password: string): Promise<Usuario> {
    logger.log('Login MOCK:', email);
    
    await new Promise(resolve => setTimeout(resolve, 1000));

    const usuario: Usuario = {
      id: 'mock-user-1',
      nombre: 'Juan',
      apellido: 'Pérez',
      email,
      dni: '12345678',
      fecha_nacimiento: '1990-01-01',
      genero: 'masculino',
      categoria_inicial: '4ta',
      rating: 1450,
      rol: 'jugador',
      createdAt: new Date().toISOString(),
    };

    return usuario;
  }

  // Registro (MOCK)
  async registerWithEmail(email: string, password: string): Promise<Usuario> {
    logger.log('Register MOCK:', email);
    
    await new Promise(resolve => setTimeout(resolve, 1000));

    const usuario: Usuario = {
      id: 'mock-user-' + Date.now(),
      nombre: '',
      apellido: '',
      email,
      dni: '',
      fecha_nacimiento: '',
      genero: 'masculino',
      categoria_inicial: '',
      rating: 1000,
      rol: 'jugador',
      createdAt: new Date().toISOString(),
    };

    return usuario;
  }

  // Completar perfil (MOCK)
  async completarPerfil(datos: PerfilCompleto): Promise<Usuario> {
    logger.log('Completar perfil MOCK:', datos);
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Simular usuario completo
    const usuario: Usuario = {
      id: 'mock-user-' + Date.now(),
      ...datos,
      email: 'user@example.com',
      rating: 1000,
      rol: 'jugador',
      createdAt: new Date().toISOString(),
    };

    return usuario;
  }

  // Actualizar perfil (MOCK)
  async actualizarPerfil(datos: Partial<Usuario>): Promise<Usuario> {
    logger.log('Actualizar perfil MOCK:', datos);
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Simular actualización
    const usuarioActualizado: Usuario = {
      id: 'mock-user-1',
      email: 'user@example.com',
      rating: 1450,
      rol: 'jugador',
      createdAt: new Date().toISOString(),
      ...datos,
    } as Usuario;

    return usuarioActualizado;
  }

  // Cambiar contraseña (MOCK)
  async cambiarPassword(passwordActual: string, passwordNueva: string): Promise<void> {
    logger.log('Cambiar password MOCK');
    await new Promise(resolve => setTimeout(resolve, 1000));
    // Simular cambio exitoso
  }

  // Verificar si el perfil está completo
  checkProfileComplete(usuario: Usuario): boolean {
    return !!(usuario.nombre && usuario.apellido && usuario.dni && usuario.categoria_inicial);
  }
}

export const authService = new AuthService();
