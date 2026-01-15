/**
 * Gestor de peticiones HTTP
 * Maneja deduplicación, retry logic y cancelación
 */

interface PendingRequest {
  promise: Promise<any>;
  controller: AbortController;
  timestamp: number;
}

class RequestManager {
  private pendingRequests: Map<string, PendingRequest>;
  private requestCounts: Map<string, number>;

  constructor() {
    this.pendingRequests = new Map();
    this.requestCounts = new Map();
  }

  /**
   * Ejecutar petición con deduplicación
   * Si ya hay una petición idéntica en curso, devuelve la misma promesa
   */
  async dedupe<T>(
    key: string,
    fetcher: (signal: AbortSignal) => Promise<T>
  ): Promise<T> {
    // Si ya hay una petición pendiente, devolver la misma
    const pending = this.pendingRequests.get(key);
    if (pending) {
      console.log(`🔄 Deduplicating request: ${key}`);
      return pending.promise;
    }

    // Crear nueva petición
    const controller = new AbortController();
    const promise = fetcher(controller.signal)
      .finally(() => {
        // Limpiar cuando termine
        this.pendingRequests.delete(key);
      });

    // Guardar como pendiente
    this.pendingRequests.set(key, {
      promise,
      controller,
      timestamp: Date.now()
    });

    // Incrementar contador
    this.requestCounts.set(key, (this.requestCounts.get(key) || 0) + 1);

    return promise;
  }

  /**
   * Cancelar petición pendiente
   */
  cancel(key: string): void {
    const pending = this.pendingRequests.get(key);
    if (pending) {
      pending.controller.abort();
      this.pendingRequests.delete(key);
      console.log(`❌ Cancelled request: ${key}`);
    }
  }

  /**
   * Cancelar todas las peticiones pendientes
   */
  cancelAll(): void {
    this.pendingRequests.forEach((pending, key) => {
      pending.controller.abort();
      console.log(`❌ Cancelled request: ${key}`);
    });
    this.pendingRequests.clear();
  }

  /**
   * Retry con exponential backoff
   */
  async retry<T>(
    fetcher: () => Promise<T>,
    options: {
      maxRetries?: number;
      initialDelay?: number;
      maxDelay?: number;
      backoffFactor?: number;
    } = {}
  ): Promise<T> {
    const {
      maxRetries = 3,
      initialDelay = 1000,
      maxDelay = 10000,
      backoffFactor = 2
    } = options;

    let lastError: Error;
    let delay = initialDelay;

    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        return await fetcher();
      } catch (error) {
        lastError = error as Error;
        
        // Si es el último intento, lanzar error
        if (attempt === maxRetries) {
          throw lastError;
        }

        // Esperar antes de reintentar
        console.log(`⏳ Retry attempt ${attempt + 1}/${maxRetries} in ${delay}ms`);
        await this.sleep(delay);
        
        // Incrementar delay con backoff
        delay = Math.min(delay * backoffFactor, maxDelay);
      }
    }

    throw lastError!;
  }

  /**
   * Batch de peticiones (ejecutar múltiples en paralelo)
   */
  async batch<T>(
    requests: Array<() => Promise<T>>,
    options: {
      concurrency?: number;
      onProgress?: (completed: number, total: number) => void;
    } = {}
  ): Promise<T[]> {
    const { concurrency = 5, onProgress } = options;
    const results: T[] = [];
    const queue = [...requests];
    let completed = 0;

    const executeNext = async (): Promise<void> => {
      const request = queue.shift();
      if (!request) return;

      try {
        const result = await request();
        results.push(result);
      } catch (error) {
        console.error('Batch request failed:', error);
        results.push(null as any);
      }

      completed++;
      onProgress?.(completed, requests.length);

      if (queue.length > 0) {
        await executeNext();
      }
    };

    // Ejecutar peticiones con concurrencia limitada
    const workers = Array(Math.min(concurrency, requests.length))
      .fill(null)
      .map(() => executeNext());

    await Promise.all(workers);
    return results;
  }

  /**
   * Helper para sleep
   */
  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Obtener estadísticas
   */
  getStats() {
    return {
      pendingRequests: this.pendingRequests.size,
      requestCounts: Object.fromEntries(this.requestCounts)
    };
  }
}

// Instancia global
export const requestManager = new RequestManager();

// Helper para generar claves de petición
export const requestKeys = {
  torneos: () => 'req-torneos',
  torneo: (id: number) => `req-torneo-${id}`,
  salas: () => 'req-salas',
  sala: (id: number) => `req-sala-${id}`,
  ranking: (type: string) => `req-ranking-${type}`,
  busqueda: (query: string) => `req-search-${query}`,
};

export default requestManager;
