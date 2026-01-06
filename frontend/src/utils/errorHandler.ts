// Utilidades para manejo de errores de manera amigable
import { logger } from './logger';
import { clientLogger } from './clientLogger';

export interface ErrorInfo {
  message: string;
  isNetworkError: boolean;
  isServerError: boolean;
  isBusinessError: boolean;
  isValidationError: boolean;
  isAuthError: boolean;
  statusCode?: number;
  errorType?: 'BusinessError' | 'ValidationError' | 'AuthenticationError' | 'AuthorizationError' | 'NotFoundError' | 'ConflictError';
}

export const parseError = (error: any): ErrorInfo => {
  logger.error('Error capturado:', error);
  
  // Log del cliente para análisis
  clientLogger.error('Error capturado en parseError', {
    message: error.message,
    status: error.response?.status,
    url: error.config?.url,
    method: error.config?.method,
    data: error.response?.data
  });

  // Error de red (sin conexión, servidor no disponible)
  if (!error.response) {
    return {
      message: getConnectionErrorMessage(),
      isNetworkError: true,
      isServerError: false,
      isBusinessError: false,
      isValidationError: false,
      isAuthError: false
    };
  }

  // Error del servidor
  const status = error.response?.status;
  const data = error.response?.data;
  const errorType = data?.error_type;

  // Errores específicos por código de estado HTTP (nuevos del backend v6.3)
  switch (status) {
    case 400:
      // BusinessError o ValidationError
      return {
        message: data?.detail || 'Los datos enviados no son válidos.',
        isNetworkError: false,
        isServerError: false,
        isBusinessError: errorType === 'BusinessError',
        isValidationError: errorType === 'ValidationError' || !errorType,
        isAuthError: false,
        statusCode: 400,
        errorType: errorType || 'ValidationError'
      };
    
    case 401:
      // AuthenticationError
      return {
        message: data?.detail || 'Tu sesión ha expirado. Por favor, inicia sesión nuevamente.',
        isNetworkError: false,
        isServerError: false,
        isBusinessError: false,
        isValidationError: false,
        isAuthError: true,
        statusCode: 401,
        errorType: 'AuthenticationError'
      };
    
    case 403:
      // AuthorizationError
      return {
        message: data?.detail || 'No tienes permisos para realizar esta acción.',
        isNetworkError: false,
        isServerError: false,
        isBusinessError: false,
        isValidationError: false,
        isAuthError: true,
        statusCode: 403,
        errorType: 'AuthorizationError'
      };
    
    case 404:
      // NotFoundError
      return {
        message: data?.detail || 'El recurso solicitado no fue encontrado.',
        isNetworkError: false,
        isServerError: false,
        isBusinessError: false,
        isValidationError: false,
        isAuthError: false,
        statusCode: 404,
        errorType: 'NotFoundError'
      };
    
    case 409:
      // ConflictError (nuevo en v6.3)
      return {
        message: data?.detail || 'Conflicto con el estado actual del recurso.',
        isNetworkError: false,
        isServerError: false,
        isBusinessError: true,
        isValidationError: false,
        isAuthError: false,
        statusCode: 409,
        errorType: 'ConflictError'
      };
    
    case 422:
      // Validation Error (FastAPI)
      return {
        message: formatValidationError(data) || 'Los datos enviados no son válidos.',
        isNetworkError: false,
        isServerError: false,
        isBusinessError: false,
        isValidationError: true,
        isAuthError: false,
        statusCode: 422,
        errorType: 'ValidationError'
      };
    
    case 500:
      return {
        message: 'Error interno del servidor. Intenta nuevamente en unos minutos.',
        isNetworkError: false,
        isServerError: true,
        isBusinessError: false,
        isValidationError: false,
        isAuthError: false,
        statusCode: 500
      };
    
    default:
      return {
        message: data?.detail || data?.message || 'Ocurrió un error inesperado. Intenta nuevamente.',
        isNetworkError: false,
        isServerError: status >= 500,
        isBusinessError: false,
        isValidationError: false,
        isAuthError: false,
        statusCode: status
      };
  }
};

// Formatear errores de validación de FastAPI
const formatValidationError = (data: any): string | null => {
  if (data?.detail && Array.isArray(data.detail)) {
    const errors = data.detail.map((err: any) => {
      const field = err.loc?.join('.') || 'campo';
      return `${field}: ${err.msg}`;
    });
    return errors.join(', ');
  }
  return data?.detail || null;
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

// Nuevas utilidades para manejar errores específicos
export const shouldRetryRequest = (errorInfo: ErrorInfo): boolean => {
  // Reintentar solo en errores de red o servidor
  return errorInfo.isNetworkError || errorInfo.isServerError;
};

export const shouldRedirectToLogin = (errorInfo: ErrorInfo): boolean => {
  // Redirigir al login solo en errores de autenticación
  return errorInfo.statusCode === 401;
};

export const getErrorColor = (errorInfo: ErrorInfo): string => {
  if (errorInfo.isAuthError) return 'text-orange-500';
  if (errorInfo.isValidationError) return 'text-yellow-500';
  if (errorInfo.isBusinessError) return 'text-blue-500';
  if (errorInfo.isServerError) return 'text-red-500';
  return 'text-red-500';
};

export const getErrorIcon = (errorInfo: ErrorInfo): string => {
  if (errorInfo.isAuthError) return '🔒';
  if (errorInfo.isValidationError) return '⚠️';
  if (errorInfo.isBusinessError) return 'ℹ️';
  if (errorInfo.isNetworkError) return '🌐';
  if (errorInfo.isServerError) return '🔥';
  return '❌';
};
