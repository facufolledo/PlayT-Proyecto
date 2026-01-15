/**
 * Sistema de Cache Inteligente
 * Maneja cache en memoria con TTL y invalidación automática
 */

interface CacheEntry<T> {
  data: T;
  timestamp: number;
  ttl: number;
}

interface CacheConfig {
  defaultTTL: number;
  maxSize: number;
  enableLogging: boolean;
}

class CacheManager {
  private cache: Map<string, CacheEntry<any>>;
  private config: CacheConfig;
  private accessCount: Map<string, number>;

  constructor(config: Partial<CacheConfig> = {}) {
    this.cache = new Map();
    this.accessCount = new Map();
    this.config = {
      defaultTTL: 5 * 60 * 1000, // 5 minutos por defecto
      maxSize: 100, // Máximo 100 entradas
      enableLogging: import.meta.env.DEV,
      ...config
    };
  }

  /**
   * Obtener dato del cache
   */
  get<T>(key: string): T | null {
    const entry = this.cache.get(key);
    
    if (!entry) {
      this.log('MISS', key);
      return null;
    }

    // Verificar si expiró
    const now = Date.now();
    if (now - entry.timestamp > entry.ttl) {
      this.log('EXPIRED', key);
      this.cache.delete(key);
      return null;
    }

    // Incrementar contador de acceso
    this.accessCount.set(key, (this.accessCount.get(key) || 0) + 1);
    this.log('HIT', key);
    
    return entry.data as T;
  }

  /**
   * Guardar dato en cache
   */
  set<T>(key: string, data: T, ttl?: number): void {
    // Si el cache está lleno, eliminar el menos usado
    if (this.cache.size >= this.config.maxSize) {
      this.evictLeastUsed();
    }

    const entry: CacheEntry<T> = {
      data,
      timestamp: Date.now(),
      ttl: ttl || this.config.defaultTTL
    };

    this.cache.set(key, entry);
    this.log('SET', key, `TTL: ${entry.ttl}ms`);
  }

  /**
   * Verificar si existe en cache y no expiró
   */
  has(key: string): boolean {
    return this.get(key) !== null;
  }

  /**
   * Invalidar una o varias claves
   */
  invalidate(keys: string | string[]): void {
    const keyArray = Array.isArray(keys) ? keys : [keys];
    
    keyArray.forEach(key => {
      // Soporta wildcards (ej: "torneo-*")
      if (key.includes('*')) {
        const regexPattern = '^' + key.replace(/\*/g, '.*') + '$';
        const pattern = new RegExp(regexPattern);
        const matchingKeys = Array.from(this.cache.keys()).filter(k => pattern.test(k));
        matchingKeys.forEach(k => {
          this.cache.delete(k);
          this.accessCount.delete(k);
        });
        this.log('INVALIDATE', `${matchingKeys.length} keys matching "${key}"`);
      } else {
        this.cache.delete(key);
        this.accessCount.delete(key);
        this.log('INVALIDATE', key);
      }
    });
  }

  /**
   * Limpiar todo el cache
   */
  clear(): void {
    const size = this.cache.size;
    this.cache.clear();
    this.accessCount.clear();
    this.log('CLEAR', `${size} entries removed`);
  }

  /**
   * Obtener o cargar dato (con cache automático)
   */
  async getOrFetch<T>(
    key: string,
    fetcher: () => Promise<T>,
    ttl?: number
  ): Promise<T> {
    // Intentar obtener del cache
    const cached = this.get<T>(key);
    if (cached !== null) {
      return cached;
    }

    // Si no está en cache, cargar
    try {
      const data = await fetcher();
      this.set(key, data, ttl);
      return data;
    } catch (error) {
      this.log('ERROR', key, error);
      throw error;
    }
  }

  /**
   * Eliminar entrada menos usada (LRU)
   */
  private evictLeastUsed(): void {
    let minAccess = Infinity;
    let lruKey: string | null = null;

    this.accessCount.forEach((count, key) => {
      if (count < minAccess) {
        minAccess = count;
        lruKey = key;
      }
    });

    if (lruKey) {
      this.cache.delete(lruKey);
      this.accessCount.delete(lruKey);
      this.log('EVICT', lruKey);
    }
  }

  /**
   * Logging condicional
   */
  private log(action: string, key: string, extra?: any): void {
    if (this.config.enableLogging) {
      const emoji: Record<string, string> = {
        HIT: '✅',
        MISS: '❌',
        SET: '💾',
        INVALIDATE: '🗑️',
        CLEAR: '🧹',
        EXPIRED: '⏰',
        EVICT: '🚮',
        ERROR: '⚠️'
      };
      
      console.log(`${emoji[action] || '📝'} Cache ${action}: ${key}`, extra || '');
    }
  }

  /**
   * Obtener estadísticas del cache
   */
  getStats() {
    return {
      size: this.cache.size,
      maxSize: this.config.maxSize,
      keys: Array.from(this.cache.keys()),
      accessCounts: Object.fromEntries(this.accessCount)
    };
  }
}

// Instancia global del cache
export const cacheManager = new CacheManager({
  defaultTTL: 5 * 60 * 1000, // 5 minutos
  maxSize: 100,
  enableLogging: import.meta.env.DEV
});

// TTLs específicos por tipo de dato
export const CACHE_TTL = {
  // Datos que cambian poco
  categorias: 30 * 60 * 1000,      // 30 minutos
  rankings: 5 * 60 * 1000,         // 5 minutos
  perfilPublico: 10 * 60 * 1000,   // 10 minutos
  
  // Datos que cambian frecuentemente
  torneos: 2 * 60 * 1000,          // 2 minutos
  salas: 1 * 60 * 1000,            // 1 minuto
  partidos: 30 * 1000,             // 30 segundos
  
  // Búsquedas y temporales
  busquedas: 10 * 60 * 1000,       // 10 minutos
  estadisticas: 5 * 60 * 1000,     // 5 minutos
  
  // Datos del usuario
  miPerfil: 15 * 60 * 1000,        // 15 minutos
  misTorneos: 2 * 60 * 1000,       // 2 minutos
  misSalas: 1 * 60 * 1000,         // 1 minuto
};

// Helper para generar claves de cache consistentes
export const cacheKeys = {
  // Rankings
  rankingGeneral: (sexo?: string) => `ranking-general-${sexo || 'all'}`,
  rankingCategoria: (categoriaId: number, sexo?: string) => 
    `ranking-cat-${categoriaId}-${sexo || 'all'}`,
  
  // Torneos
  torneos: () => 'torneos-list',
  torneo: (id: number) => `torneo-${id}`,
  torneosParejas: (torneoId: number) => `torneo-${torneoId}-parejas`,
  torneosZonas: (torneoId: number) => `torneo-${torneoId}-zonas`,
  torneosPartidos: (torneoId: number) => `torneo-${torneoId}-partidos`,
  misTorneos: () => 'mis-torneos',
  
  // Salas
  salas: () => 'salas-list',
  sala: (id: number) => `sala-${id}`,
  misSalas: () => 'mis-salas',
  
  // Perfiles
  perfil: (username: string) => `perfil-${username}`,
  perfilId: (id: number) => `perfil-id-${id}`,
  estadisticas: (userId: number) => `stats-${userId}`,
  
  // Búsquedas
  busqueda: (query: string) => `search-${query.toLowerCase().trim()}`,
  
  // Categorías
  categorias: () => 'categorias-sistema',
};

export default cacheManager;
