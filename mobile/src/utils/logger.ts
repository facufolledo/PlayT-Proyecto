// Logger utility - solo muestra en desarrollo
const isDev = __DEV__;

export const logger = {
  log: (...args: any[]) => {
    if (isDev) console.log('[PlayR]', ...args);
  },
  error: (...args: any[]) => {
    if (isDev) console.error('[PlayR ERROR]', ...args);
  },
  warn: (...args: any[]) => {
    if (isDev) console.warn('[PlayR WARN]', ...args);
  },
  info: (...args: any[]) => {
    if (isDev) console.info('[PlayR INFO]', ...args);
  }
};
