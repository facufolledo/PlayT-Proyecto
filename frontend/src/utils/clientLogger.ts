interface LogLevel {
  DEBUG: 0;
  INFO: 1;
  WARN: 2;
  ERROR: 3;
}

const LOG_LEVELS: LogLevel = {
  DEBUG: 0,
  INFO: 1,
  WARN: 2,
  ERROR: 3
};

interface LogEntry {
  timestamp: string;
  level: keyof LogLevel;
  message: string;
  data?: any;
  userId?: string;
  sessionId: string;
  url: string;
  userAgent: string;
}

class ClientLogger {
  private logs: LogEntry[] = [];
  private maxLogs = 100;
  private sessionId: string;
  private currentLogLevel: keyof LogLevel;
  private apiUrl: string;

  constructor() {
    this.sessionId = this.generateSessionId();
    this.currentLogLevel = import.meta.env.DEV ? 'DEBUG' : 'WARN';
    this.apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    
    // Capturar errores no manejados
    this.setupGlobalErrorHandlers();
  }

  private generateSessionId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  private setupGlobalErrorHandlers() {
    // Errores de JavaScript
    window.addEventListener('error', (event) => {
      this.error('Uncaught Error', {
        message: event.message,
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
        stack: event.error?.stack
      });
    });

    // Promesas rechazadas no manejadas
    window.addEventListener('unhandledrejection', (event) => {
      this.error('Unhandled Promise Rejection', {
        reason: event.reason,
        promise: event.promise
      });
    });
  }

  private shouldLog(level: keyof LogLevel): boolean {
    return LOG_LEVELS[level] >= LOG_LEVELS[this.currentLogLevel];
  }

  private createLogEntry(level: keyof LogLevel, message: string, data?: any): LogEntry {
    const userId = localStorage.getItem('userId') || undefined;
    
    return {
      timestamp: new Date().toISOString(),
      level,
      message,
      data,
      userId,
      sessionId: this.sessionId,
      url: window.location.href,
      userAgent: navigator.userAgent
    };
  }

  private addLog(entry: LogEntry) {
    this.logs.push(entry);
    
    // Mantener solo los últimos maxLogs
    if (this.logs.length > this.maxLogs) {
      this.logs = this.logs.slice(-this.maxLogs);
    }

    // En desarrollo, también loggear en consola
    if (import.meta.env.DEV) {
      const consoleMethod = entry.level.toLowerCase() as 'debug' | 'info' | 'warn' | 'error';
      console[consoleMethod](`[${entry.timestamp}] ${entry.message}`, entry.data || '');
    }
  }

  debug(message: string, data?: any) {
    if (!this.shouldLog('DEBUG')) return;
    this.addLog(this.createLogEntry('DEBUG', message, data));
  }

  info(message: string, data?: any) {
    if (!this.shouldLog('INFO')) return;
    this.addLog(this.createLogEntry('INFO', message, data));
  }

  warn(message: string, data?: any) {
    if (!this.shouldLog('WARN')) return;
    this.addLog(this.createLogEntry('WARN', message, data));
  }

  error(message: string, data?: any) {
    if (!this.shouldLog('ERROR')) return;
    this.addLog(this.createLogEntry('ERROR', message, data));
    
    // Enviar errores críticos al servidor inmediatamente
    this.sendErrorToServer(this.createLogEntry('ERROR', message, data));
  }

  // Métodos específicos para diferentes tipos de eventos
  userAction(action: string, data?: any) {
    this.info(`User Action: ${action}`, data);
  }

  apiCall(method: string, url: string, status?: number, duration?: number) {
    const message = `API ${method} ${url}`;
    const logData = { status, duration };
    
    if (status && status >= 400) {
      this.warn(message, logData);
    } else {
      this.debug(message, logData);
    }
  }

  performance(metric: string, value: number, unit: string = 'ms') {
    this.debug(`Performance: ${metric}`, { value, unit });
  }

  // Enviar logs al servidor
  async sendLogsToServer() {
    if (this.logs.length === 0) return;

    try {
      const token = localStorage.getItem('token') || localStorage.getItem('firebase_token');
      
      await fetch(`${this.apiUrl}/logs/client`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { Authorization: `Bearer ${token}` })
        },
        body: JSON.stringify({
          logs: this.logs,
          sessionId: this.sessionId
        })
      });

      // Limpiar logs enviados
      this.logs = [];
    } catch (error) {
      console.error('Error sending logs to server:', error);
    }
  }

  private async sendErrorToServer(logEntry: LogEntry) {
    try {
      const token = localStorage.getItem('token') || localStorage.getItem('firebase_token');
      
      await fetch(`${this.apiUrl}/logs/error`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { Authorization: `Bearer ${token}` })
        },
        body: JSON.stringify(logEntry)
      });
    } catch (error) {
      console.error('Error sending error to server:', error);
    }
  }

  // Obtener logs para debugging
  getLogs(): LogEntry[] {
    return [...this.logs];
  }

  // Limpiar logs
  clearLogs() {
    this.logs = [];
  }

  // Cambiar nivel de log
  setLogLevel(level: keyof LogLevel) {
    this.currentLogLevel = level;
  }
}

// Instancia singleton
export const clientLogger = new ClientLogger();

// Enviar logs al servidor cada 30 segundos
setInterval(() => {
  clientLogger.sendLogsToServer();
}, 30000);

// Enviar logs antes de cerrar la página
window.addEventListener('beforeunload', () => {
  clientLogger.sendLogsToServer();
});