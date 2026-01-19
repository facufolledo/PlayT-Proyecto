/**
 * Parsea una fecha ISO (YYYY-MM-DD) sin problemas de zona horaria.
 * 
 * El problema: new Date("2026-01-23") interpreta la fecha como UTC medianoche,
 * y al convertirla a hora local puede retroceder un día (ej: en UTC-3 se convierte
 * a 2026-01-22 21:00).
 * 
 * La solución: Parsear manualmente usando new Date(year, month-1, day) que siempre
 * usa hora local.
 * 
 * @param fechaISO - Fecha en formato ISO (YYYY-MM-DD)
 * @returns Date object en hora local
 */
export function parseFechaSinZonaHoraria(fechaISO: string): Date {
  const [year, month, day] = fechaISO.split('-').map(Number);
  return new Date(year, month - 1, day);
}

/**
 * Formatea una fecha ISO para mostrar en español.
 * 
 * @param fechaISO - Fecha en formato ISO (YYYY-MM-DD)
 * @param options - Opciones de formato (por defecto: día y mes corto)
 * @returns Fecha formateada en español
 */
export function formatearFecha(
  fechaISO: string,
  options: Intl.DateTimeFormatOptions = { day: 'numeric', month: 'short' }
): string {
  return parseFechaSinZonaHoraria(fechaISO).toLocaleDateString('es-ES', options);
}

/**
 * Formatea un rango de fechas ISO para mostrar en español.
 * 
 * @param fechaInicio - Fecha de inicio en formato ISO (YYYY-MM-DD)
 * @param fechaFin - Fecha de fin en formato ISO (YYYY-MM-DD)
 * @returns Rango de fechas formateado (ej: "23 ene - 25 ene 2026")
 */
export function formatearRangoFechas(fechaInicio: string, fechaFin: string): string {
  const inicio = formatearFecha(fechaInicio, { day: 'numeric', month: 'short' });
  const fin = formatearFecha(fechaFin, { day: 'numeric', month: 'short', year: 'numeric' });
  return `${inicio} - ${fin}`;
}
