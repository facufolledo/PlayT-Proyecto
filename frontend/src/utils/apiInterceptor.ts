import axios, { AxiosError, AxiosRequestConfig, AxiosResponse } from 'axios';
import { clientLogger } from './clientLogger';

interface RetryConfig {
  retries: number;
  retryDelay: number;
  retryCondition?: (error: AxiosError) => boolean;
}

const DEFAULT_RETRY_CONFIG: RetryConfig = {
  retries: 3,
  retryDelay: 1000,
  retryCondition: (error: AxiosError) => {
    // Retry en errores de red o servidor (5xx)
    return !error.response || (error.response.status >= 500 && error.response.status < 600);
  }
};

// Función para delay con backoff exponencial
const delay = (ms: number, attempt: number) => 
  new Promise(resolve => setTimeout(resolve, ms * Math.pow(2, attempt - 1)));

// Función para retry de requests
const retryRequest = async (
  originalRequest: AxiosRequestConfig & { _retry?: boolean; _retryCount?: number },
  config: RetryConfig = DEFAULT_RETRY_CONFIG
): Promise<AxiosResponse> => {
  const { retries, retryDelay, retryCondition } = config;
  
  if (!originalRequest._retryCount) {
    originalRequest._retryCount = 0;
  }

  return new Promise((resolve, reject) => {
    const makeRequest = async () => {
      try {
        const response = await axios(originalRequest);
        resolve(response);
      } catch (error: any) {
        const shouldRetry = originalRequest._retryCount! < retries && 
                           retryCondition!(error) && 
                           !originalRequest._retry;

        if (shouldRetry) {
          originalRequest._retryCount!++;
          originalRequest._retry = true;

          clientLogger.warn(`Request retry attempt ${originalRequest._retryCount}`, {
            url: originalRequest.url,
            method: originalRequest.method,
            attempt: originalRequest._retryCount,
            error: error.message
          });

          await delay(retryDelay, originalRequest._retryCount!);
          makeRequest();
        } else {
          clientLogger.error('Request failed after all retries', {
            url: originalRequest.url,
            method: originalRequest.method,
            totalAttempts: originalRequest._retryCount! + 1,
            error: error.message
          });
          reject(error);
        }
      }
    };

    makeRequest();
  });
};

// Configurar interceptor de respuesta para retry automático
export const setupRetryInterceptor = () => {
  axios.interceptors.response.use(
    (response: AxiosResponse) => {
      // Log successful requests
      clientLogger.apiCall(
        response.config.method?.toUpperCase() || 'GET',
        response.config.url || '',
        response.status,
        Date.now() - (response.config as any).startTime
      );
      return response;
    },
    async (error: AxiosError) => {
      const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean; _retryCount?: number };

      if (originalRequest && !originalRequest._retry) {
        try {
          return await retryRequest(originalRequest);
        } catch (retryError) {
          return Promise.reject(retryError);
        }
      }

      return Promise.reject(error);
    }
  );

  // Interceptor de request para timing
  axios.interceptors.request.use((config) => {
    (config as any).startTime = Date.now();
    return config;
  });
};

// Función para requests con retry manual
export const requestWithRetry = async <T = any>(
  requestConfig: AxiosRequestConfig,
  retryConfig?: Partial<RetryConfig>
): Promise<AxiosResponse<T>> => {
  const config = { ...DEFAULT_RETRY_CONFIG, ...retryConfig };
  return retryRequest(requestConfig, config);
};

// Hook para requests con retry
export const useRetryRequest = () => {
  const makeRequest = async <T = any>(
    requestConfig: AxiosRequestConfig,
    retryConfig?: Partial<RetryConfig>
  ): Promise<T> => {
    try {
      const response = await requestWithRetry<T>(requestConfig, retryConfig);
      return response.data;
    } catch (error) {
      throw error;
    }
  };

  return { makeRequest };
};