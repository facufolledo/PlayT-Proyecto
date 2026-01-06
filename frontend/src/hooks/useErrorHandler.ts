import { useState, useCallback } from 'react';
import { ErrorInfo, parseError } from '../utils/errorHandler';

export const useErrorHandler = () => {
  const [error, setError] = useState<ErrorInfo | null>(null);

  const handleError = useCallback((err: any) => {
    const errorInfo = parseError(err);
    setError(errorInfo);
    
    // Auto-cerrar después de 5 segundos para errores no críticos
    if (!errorInfo.isNetworkError && !errorInfo.isServerError) {
      setTimeout(() => setError(null), 5000);
    }
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    error,
    handleError,
    clearError
  };
};
