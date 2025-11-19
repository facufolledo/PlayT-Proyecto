import { logger } from '../utils/logger';

type WebSocketEventType =
  | 'connected'
  | 'jugador_unido'
  | 'equipos_asignados'
  | 'partido_iniciado'
  | 'marcador_actualizado'
  | 'resultado_reportado'
  | 'resultado_confirmado'
  | 'pong';

interface WebSocketMessage {
  type: WebSocketEventType;
  data?: any;
  message?: string;
  sala_id?: number;
}

type EventCallback = (data: any) => void;

class WebSocketService {
  private ws: WebSocket | null = null;
  private salaId: string | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 3000;
  private pingInterval: NodeJS.Timeout | null = null;
  private eventListeners: Map<WebSocketEventType, EventCallback[]> = new Map();
  private isIntentionalClose = false;

  /**
   * Conectar a una sala específica
   */
  connect(salaId: string) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      logger.log('WebSocket ya está conectado');
      return;
    }

    this.salaId = salaId;
    this.isIntentionalClose = false;
    
    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';
    const url = `${wsUrl}/ws/salas/${salaId}`;

    logger.log('Conectando WebSocket a:', url);

    try {
      this.ws = new WebSocket(url);

      this.ws.onopen = () => {
        logger.log('WebSocket conectado a sala:', salaId);
        this.reconnectAttempts = 0;
        this.startPing();
      };

      this.ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          logger.log('WebSocket mensaje recibido:', message);
          this.handleMessage(message);
        } catch (error) {
          logger.error('Error parseando mensaje WebSocket:', error);
        }
      };

      this.ws.onerror = (error) => {
        logger.error('WebSocket error:', error);
      };

      this.ws.onclose = (event) => {
        logger.log('WebSocket cerrado:', event.code, event.reason);
        this.stopPing();

        // Intentar reconectar si no fue un cierre intencional
        if (!this.isIntentionalClose && this.reconnectAttempts < this.maxReconnectAttempts) {
          this.reconnectAttempts++;
          logger.log(`Intentando reconectar (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
          
          setTimeout(() => {
            if (this.salaId) {
              this.connect(this.salaId);
            }
          }, this.reconnectDelay);
        }
      };
    } catch (error) {
      logger.error('Error creando WebSocket:', error);
    }
  }

  /**
   * Desconectar WebSocket
   */
  disconnect() {
    this.isIntentionalClose = true;
    this.stopPing();
    
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    
    this.salaId = null;
    this.reconnectAttempts = 0;
    logger.log('WebSocket desconectado');
  }

  /**
   * Enviar ping para mantener conexión viva
   */
  private startPing() {
    this.stopPing();
    
    this.pingInterval = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send('ping');
      }
    }, 30000); // Ping cada 30 segundos
  }

  /**
   * Detener ping
   */
  private stopPing() {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
  }

  /**
   * Manejar mensajes recibidos
   */
  private handleMessage(message: WebSocketMessage) {
    const listeners = this.eventListeners.get(message.type);
    
    if (listeners) {
      listeners.forEach(callback => {
        try {
          callback(message.data || message);
        } catch (error) {
          logger.error('Error en callback de evento:', error);
        }
      });
    }
  }

  /**
   * Suscribirse a un evento
   */
  on(event: WebSocketEventType, callback: EventCallback) {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, []);
    }
    
    this.eventListeners.get(event)!.push(callback);
    
    // Retornar función para desuscribirse
    return () => {
      const listeners = this.eventListeners.get(event);
      if (listeners) {
        const index = listeners.indexOf(callback);
        if (index > -1) {
          listeners.splice(index, 1);
        }
      }
    };
  }

  /**
   * Desuscribirse de un evento
   */
  off(event: WebSocketEventType, callback?: EventCallback) {
    if (!callback) {
      // Eliminar todos los listeners del evento
      this.eventListeners.delete(event);
    } else {
      // Eliminar listener específico
      const listeners = this.eventListeners.get(event);
      if (listeners) {
        const index = listeners.indexOf(callback);
        if (index > -1) {
          listeners.splice(index, 1);
        }
      }
    }
  }

  /**
   * Verificar si está conectado
   */
  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }
}

// Instancia singleton
export const websocketService = new WebSocketService();
