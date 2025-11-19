import { io, Socket } from 'socket.io-client';
import { logger } from '../utils/logger';

const SOCKET_URL = process.env.EXPO_PUBLIC_SOCKET_URL || 'http://localhost:3000';

interface ScoreUpdate {
  salaId: number;
  equipo1Puntos: number;
  equipo2Puntos: number;
  equipo1Sets: number;
  equipo2Sets: number;
  estado: string;
}

interface PartidoFinalizado {
  salaId: number;
  ganador: string;
  resultado: string;
}

class WebSocketService {
  private socket: Socket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;

  // Conectar al servidor WebSocket
  connect(token: string): void {
    if (this.socket?.connected) {
      logger.log('WebSocket ya está conectado');
      return;
    }

    logger.log('Conectando a WebSocket:', SOCKET_URL);

    this.socket = io(SOCKET_URL, {
      auth: { token },
      transports: ['websocket'],
      reconnection: true,
      reconnectionAttempts: this.maxReconnectAttempts,
      reconnectionDelay: this.reconnectDelay,
    });

    this.setupEventListeners();
  }

  // Configurar listeners de eventos
  private setupEventListeners(): void {
    if (!this.socket) return;

    this.socket.on('connect', () => {
      logger.log('WebSocket conectado');
      this.reconnectAttempts = 0;
    });

    this.socket.on('disconnect', (reason) => {
      logger.log('WebSocket desconectado:', reason);
    });

    this.socket.on('connect_error', (error) => {
      logger.error('Error de conexión WebSocket:', error);
      this.reconnectAttempts++;
      
      if (this.reconnectAttempts >= this.maxReconnectAttempts) {
        logger.error('Máximo de intentos de reconexión alcanzado');
      }
    });

    this.socket.on('error', (error) => {
      logger.error('Error WebSocket:', error);
    });
  }

  // Unirse a una sala
  joinSala(salaId: number): void {
    if (!this.socket?.connected) {
      logger.error('WebSocket no está conectado');
      return;
    }

    logger.log('Uniéndose a sala:', salaId);
    this.socket.emit('join-sala', { salaId });
  }

  // Salir de una sala
  leaveSala(salaId: number): void {
    if (!this.socket?.connected) {
      logger.error('WebSocket no está conectado');
      return;
    }

    logger.log('Saliendo de sala:', salaId);
    this.socket.emit('leave-sala', { salaId });
  }

  // Actualizar marcador
  updateScore(data: ScoreUpdate): void {
    if (!this.socket?.connected) {
      logger.error('WebSocket no está conectado');
      return;
    }

    logger.log('Actualizando marcador:', data);
    this.socket.emit('update-score', data);
  }

  // Finalizar partido
  finalizarPartido(data: PartidoFinalizado): void {
    if (!this.socket?.connected) {
      logger.error('WebSocket no está conectado');
      return;
    }

    logger.log('Finalizando partido:', data);
    this.socket.emit('finalizar-partido', data);
  }

  // Escuchar actualizaciones de marcador
  onScoreUpdate(callback: (data: ScoreUpdate) => void): void {
    if (!this.socket) return;
    this.socket.on('score-updated', callback);
  }

  // Escuchar partido finalizado
  onPartidoFinalizado(callback: (data: PartidoFinalizado) => void): void {
    if (!this.socket) return;
    this.socket.on('partido-finalizado', callback);
  }

  // Escuchar jugador unido
  onJugadorUnido(callback: (data: any) => void): void {
    if (!this.socket) return;
    this.socket.on('jugador-unido', callback);
  }

  // Escuchar jugador salió
  onJugadorSalio(callback: (data: any) => void): void {
    if (!this.socket) return;
    this.socket.on('jugador-salio', callback);
  }

  // Remover listener
  off(event: string, callback?: (...args: any[]) => void): void {
    if (!this.socket) return;
    if (callback) {
      this.socket.off(event, callback);
    } else {
      this.socket.off(event);
    }
  }

  // Desconectar
  disconnect(): void {
    if (this.socket) {
      logger.log('Desconectando WebSocket');
      this.socket.disconnect();
      this.socket = null;
    }
  }

  // Verificar si está conectado
  isConnected(): boolean {
    return this.socket?.connected || false;
  }

  // Obtener socket (para casos especiales)
  getSocket(): Socket | null {
    return this.socket;
  }
}

export const websocketService = new WebSocketService();
