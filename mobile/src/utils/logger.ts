// Logger utility - solo muestra en desarrollo
const isDev = __DEV__;

export const logger = {
  log: (...args: any[]) => {
    if (isDev) console.log('[Drive+]', ...args);
  },
  error: (...args: any[]) => {
    if (isDev) console.error('[Drive+ ERROR]', ...args);
  },
  warn: (...args: any[]) => {
    if (isDev) console.warn('[Drive+ WARN]', ...args);
  },
  info: (...args: any[]) => {
    if (isDev) console.info('[Drive+ INFO]', ...args);
  }
};
