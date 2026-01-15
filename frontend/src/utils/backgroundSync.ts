/**
 * Background Sync Manager
 * Maneja sincronización de datos cuando el usuario está offline
 */

interface PendingAction {
  id: string;
  type: 'torneo' | 'inscripcion' | 'resultado' | 'sala';
  data: any;
  timestamp: number;
  retries: number;
}

class BackgroundSyncManager {
  private dbName = 'drive-plus-sync';
  private dbVersion = 1;
  private db: IDBDatabase | null = null;

  constructor() {
    this.initDB();
  }

  /**
   * Inicializar IndexedDB
   */
  private async initDB(): Promise<void> {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, this.dbVersion);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        this.db = request.result;
        resolve();
      };

      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;

        // Crear stores si no existen
        if (!db.objectStoreNames.contains('torneos')) {
          db.createObjectStore('torneos', { keyPath: 'id' });
        }
        if (!db.objectStoreNames.contains('inscripciones')) {
          db.createObjectStore('inscripciones', { keyPath: 'id' });
        }
        if (!db.objectStoreNames.contains('resultados')) {
          db.createObjectStore('resultados', { keyPath: 'id' });
        }
      };
    });
  }

  /**
   * Guardar acción pendiente
   */
  async savePendingAction(
    type: PendingAction['type'],
    data: any
  ): Promise<string> {
    await this.ensureDB();

    const action: PendingAction = {
      id: `${type}-${Date.now()}-${Math.random()}`,
      type,
      data,
      timestamp: Date.now(),
      retries: 0
    };

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([`${type}s`], 'readwrite');
      const store = transaction.objectStore(`${type}s`);
      const request = store.add(action);

      request.onsuccess = () => {
        console.log(`💾 Saved pending ${type}:`, action.id);
        resolve(action.id);
      };
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Obtener acciones pendientes
   */
  async getPendingActions(type: PendingAction['type']): Promise<PendingAction[]> {
    await this.ensureDB();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([`${type}s`], 'readonly');
      const store = transaction.objectStore(`${type}s`);
      const request = store.getAll();

      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Eliminar acción pendiente
   */
  async removePendingAction(
    type: PendingAction['type'],
    id: string
  ): Promise<void> {
    await this.ensureDB();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([`${type}s`], 'readwrite');
      const store = transaction.objectStore(`${type}s`);
      const request = store.delete(id);

      request.onsuccess = () => {
        console.log(`✅ Removed pending ${type}:`, id);
        resolve();
      };
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Registrar sync con Service Worker
   */
  async registerSync(tag: string): Promise<void> {
    if ('serviceWorker' in navigator && 'SyncManager' in window) {
      try {
        const registration = await navigator.serviceWorker.ready;
        // @ts-ignore - Background Sync API no está en todos los tipos de TS
        await registration.sync?.register(tag);
        console.log(`🔄 Registered background sync: ${tag}`);
      } catch (error) {
        console.error('Background sync registration failed:', error);
        // Fallback: intentar sincronizar inmediatamente
        this.syncNow(tag);
      }
    } else {
      console.warn('Background Sync not supported, syncing immediately');
      this.syncNow(tag);
    }
  }

  /**
   * Sincronizar inmediatamente (fallback)
   */
  private async syncNow(tag: string): Promise<void> {
    // Implementar lógica de sincronización inmediata
    console.log(`⚡ Syncing immediately: ${tag}`);
  }

  /**
   * Asegurar que DB está inicializada
   */
  private async ensureDB(): Promise<void> {
    if (!this.db) {
      await this.initDB();
    }
  }

  /**
   * Verificar si hay acciones pendientes
   */
  async hasPendingActions(): Promise<boolean> {
    await this.ensureDB();

    const types: PendingAction['type'][] = ['torneo', 'inscripcion', 'resultado'];
    
    for (const type of types) {
      const actions = await this.getPendingActions(type);
      if (actions.length > 0) return true;
    }
    
    return false;
  }

  /**
   * Obtener contador de acciones pendientes
   */
  async getPendingCount(): Promise<number> {
    await this.ensureDB();

    const types: PendingAction['type'][] = ['torneo', 'inscripcion', 'resultado'];
    let count = 0;
    
    for (const type of types) {
      const actions = await this.getPendingActions(type);
      count += actions.length;
    }
    
    return count;
  }
}

// Instancia global
export const backgroundSync = new BackgroundSyncManager();

// Helpers para uso fácil
export const syncHelpers = {
  /**
   * Guardar torneo para sincronizar después
   */
  async saveTorneoOffline(torneoData: any): Promise<string> {
    const id = await backgroundSync.savePendingAction('torneo', torneoData);
    await backgroundSync.registerSync('sync-torneos');
    return id;
  },

  /**
   * Guardar inscripción para sincronizar después
   */
  async saveInscripcionOffline(torneoId: number, inscripcionData: any): Promise<string> {
    const id = await backgroundSync.savePendingAction('inscripcion', {
      torneoId,
      ...inscripcionData
    });
    await backgroundSync.registerSync('sync-inscripciones');
    return id;
  },

  /**
   * Guardar resultado para sincronizar después
   */
  async saveResultadoOffline(salaId: number, resultadoData: any): Promise<string> {
    const id = await backgroundSync.savePendingAction('resultado', {
      salaId,
      ...resultadoData
    });
    await backgroundSync.registerSync('sync-resultados');
    return id;
  }
};

export default backgroundSync;
