// Utilidades para manejo de errores de manera amigable
import { logger } from './logger';

export interface ErrorInfo {
  message: string;
  isNetworkError: boolean;
  isServerError: boolean;
  statusCode?: number;
}

export const parseError = (error: any): ErrorInfo => {
  logger.error('Error capturado:', error);

  // Error de red (sin conexión, servidor no disponible)
  if (!error.response) {
    return {
      message: 'No se pudo conectar con el servidor. Verifica tu conexión a internet.',
      isNetworkError: true,
      isServerError: false
    };
  }

  // Error del servidor
  const status = error.response?.status;
  const data = error.response?.data;

  // Errores específicos por código de estado
  switch (status) {
    case 401:
      return {
        message: 'Tu sesión ha expirado. Por favor, inicia sesión nuevamente.',
        isNetworkError: false,
        isServerError: false,
        statusCode: 401
      };
    
    case 403:
      return {
        message: 'No tienes permisos para realizar esta acción.',
        isNetworkError: false,
        isServerError: false,
        statusCode: 403
      };
    
    case 404:
      return {
        message: data?.detail || 'El recurso solicitado no fue encontrado.',
        isNetworkError: false,
        isServerError: false,
        statusCode: 404
      };
    
    case 422:
      return {
        message: data?.detail || 'Los datos enviados no son válidos.',
        isNetworkError: false,
        isServerError: false,
        statusCode: 422
      };
    
    case 500:
      return {
        message: 'Error interno del servidor. Intenta nuevamente en unos minutos.',
        isNetworkError: false,
        isServerError: true,
        statusCode: 500
      };
    
    default:
      return {
        message: data?.detail || data?.message || 'Ocurrió un error inesperado. Intenta nuevamente.',
        isNetworkError: false,
        isServerError: status >= 500,
        statusCode: status
      };
  }
};

export const getConnectionErrorMessage = (): string => {
  const isDev = import.meta.env.DEV;
  
  if (isDev) {
    return 'No se pudo conectar con el servidor de desarrollo. Verifica que el backend esté ejecutándose.';
  }
  
  return 'No se pudo conectar con el servidor. Verifica tu conexión a internet e intenta nuevamente.';
};

export const getServerErrorMessage = (statusCode?: number): string => {
  if (statusCode === 500) {
    return 'El servidor está experimentando problemas. Intenta nuevamente en unos minutos.';
  }
  
  return 'Ocurrió un error en el servidor. Si el problema persiste, contacta al soporte.';
};