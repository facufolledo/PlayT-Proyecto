import { Clock, Trash2, Plus } from 'lucide-react';

interface FranjaRestriccion {
  dias: string[];
  horaInicio: string;
  horaFin: string;
}

interface SelectorDisponibilidadProps {
  value: FranjaRestriccion[];
  onChange: (restricciones: FranjaRestriccion[]) => void;
  fechaInicio: string; // ISO date string
  fechaFin: string; // ISO date string
  horariosDisponibles?: {
    [dia: string]: { inicio: string; fin: string };
  };
}

const TODOS_LOS_DIAS = [
  { value: 'lunes', label: 'Lun', dayOfWeek: 1 },
  { value: 'martes', label: 'Mar', dayOfWeek: 2 },
  { value: 'miercoles', label: 'Mié', dayOfWeek: 3 },
  { value: 'jueves', label: 'Jue', dayOfWeek: 4 },
  { value: 'viernes', label: 'Vie', dayOfWeek: 5 },
  { value: 'sabado', label: 'Sáb', dayOfWeek: 6 },
  { value: 'domingo', label: 'Dom', dayOfWeek: 0 },
];

// Generar horarios cada 30 minutos
const HORARIOS_DISPONIBLES = (() => {
  const horarios: string[] = [];
  for (let h = 0; h < 24; h++) {
    const hora = h.toString().padStart(2, '0');
    horarios.push(`${hora}:00`);
    horarios.push(`${hora}:30`);
  }
  return horarios;
})();

// Función para calcular qué días de la semana están entre dos fechas
function calcularDiasDisponibles(fechaInicio: string, fechaFin: string): string[] {
  // Parsear fechas en hora local para evitar problemas de zona horaria
  const [yearI, monthI, dayI] = fechaInicio.split('-').map(Number);
  const [yearF, monthF, dayF] = fechaFin.split('-').map(Number);
  
  const inicio = new Date(yearI, monthI - 1, dayI);
  const fin = new Date(yearF, monthF - 1, dayF);
  const diasEncontrados = new Set<number>();
  
  // Iterar desde fecha inicio hasta fecha fin
  const current = new Date(inicio);
  while (current <= fin) {
    diasEncontrados.add(current.getDay());
    current.setDate(current.getDate() + 1);
  }
  
  // Convertir números de día a nombres
  return TODOS_LOS_DIAS
    .filter(dia => diasEncontrados.has(dia.dayOfWeek))
    .map(dia => dia.value);
}

export default function SelectorDisponibilidad({
  value,
  onChange,
  fechaInicio,
  fechaFin,
  horariosDisponibles
}: SelectorDisponibilidadProps) {
  // Calcular días disponibles según las fechas del torneo
  const diasDisponibles = calcularDiasDisponibles(fechaInicio, fechaFin);
  const DIAS = TODOS_LOS_DIAS.filter(dia => diasDisponibles.includes(dia.value));

  // Función para generar horarios basados en los horarios del torneo
  const generarHorariosDelTorneo = (): string[] => {
    if (!horariosDisponibles) {
      // Si no hay horarios específicos, usar todos los horarios
      return HORARIOS_DISPONIBLES;
    }

    // Verificar si es un array (formato viejo) o un objeto (formato nuevo)
    if (Array.isArray(horariosDisponibles)) {
      // Formato viejo: array de horarios
      return HORARIOS_DISPONIBLES;
    }

    // Formato nuevo: objeto con días y horarios
    try {
      // Encontrar el rango más amplio de todos los días
      let horaMinima = '23:59';
      let horaMaxima = '00:00';

      Object.values(horariosDisponibles).forEach((horario: any) => {
        if (horario && typeof horario === 'object') {
          const inicio = horario.inicio || horario.hora_inicio;
          const fin = horario.fin || horario.hora_fin;
          
          if (inicio && inicio < horaMinima) horaMinima = inicio;
          if (fin && fin > horaMaxima) horaMaxima = fin;
        }
      });

      // Si no se encontraron horarios válidos, usar todos
      if (horaMinima === '23:59' || horaMaxima === '00:00') {
        return HORARIOS_DISPONIBLES;
      }

      // Generar horarios cada 30 minutos dentro del rango
      const horarios: string[] = [];
      const [horaMin, minMin] = horaMinima.split(':').map(Number);
      const [horaMax, minMax] = horaMaxima.split(':').map(Number);
      
      let horaActual = horaMin;
      let minActual = minMin;

      while (horaActual < horaMax || (horaActual === horaMax && minActual <= minMax)) {
        const horaStr = horaActual.toString().padStart(2, '0');
        const minStr = minActual.toString().padStart(2, '0');
        horarios.push(`${horaStr}:${minStr}`);
        
        minActual += 30;
        if (minActual >= 60) {
          minActual = 0;
          horaActual++;
        }
      }

      return horarios.length > 0 ? horarios : HORARIOS_DISPONIBLES;
    } catch (error) {
      console.error('Error generando horarios del torneo:', error);
      return HORARIOS_DISPONIBLES;
    }
  };

  const horariosParaMostrar = generarHorariosDelTorneo();

  const agregarFranja = () => {
    if (value.length < 3) { // Permitir más restricciones
      onChange([...value, { dias: [], horaInicio: '', horaFin: '' }]);
    }
  };

  const eliminarFranja = (index: number) => {
    onChange(value.filter((_, i) => i !== index));
  };

  const toggleDia = (franjaIndex: number, dia: string) => {
    const nuevasRestricciones = [...value];
    const franja = nuevasRestricciones[franjaIndex];
    
    if (franja.dias.includes(dia)) {
      franja.dias = franja.dias.filter(d => d !== dia);
    } else {
      franja.dias = [...franja.dias, dia];
    }
    
    onChange(nuevasRestricciones);
  };

  const cambiarHoraInicio = (franjaIndex: number, hora: string) => {
    const nuevasRestricciones = [...value];
    nuevasRestricciones[franjaIndex].horaInicio = hora;
    // Si la hora de fin es anterior a la nueva hora de inicio, resetearla
    if (nuevasRestricciones[franjaIndex].horaFin && nuevasRestricciones[franjaIndex].horaFin <= hora) {
      nuevasRestricciones[franjaIndex].horaFin = '';
    }
    onChange(nuevasRestricciones);
  };

  const cambiarHoraFin = (franjaIndex: number, hora: string) => {
    const nuevasRestricciones = [...value];
    nuevasRestricciones[franjaIndex].horaFin = hora;
    onChange(nuevasRestricciones);
  };

  // Función para obtener horarios válidos para "Hasta" basado en "Desde"
  const getHorariosFinValidos = (horaInicio: string): string[] => {
    if (!horaInicio) return horariosParaMostrar;
    return horariosParaMostrar.filter(hora => hora > horaInicio);
  };

  return (
    <div className="space-y-4">
      {/* Header mejorado */}
      <div className="bg-gradient-to-r from-blue-50 to-blue-100 border border-blue-300 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <Clock size={20} className="text-blue-600 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <h3 className="text-sm font-bold text-blue-900 mb-1">
              Restricciones Horarias (Opcional)
            </h3>
            <p className="text-xs text-blue-700">
              Solo especifica los horarios que <strong>NO puedes jugar</strong>. 
              El resto del tiempo estarás disponible automáticamente.
            </p>
          </div>
        </div>
      </div>

      {/* Estado sin restricciones */}
      {value.length === 0 && (
        <div className="bg-green-50 border-2 border-green-300 rounded-lg p-4 text-center">
          <div className="text-3xl mb-2">✅</div>
          <p className="text-sm text-green-800 font-bold mb-1">
            Sin restricciones
          </p>
          <p className="text-xs text-green-700">
            Disponible en todos los horarios del torneo
          </p>
        </div>
      )}

      {/* Restricciones */}
      {value.map((franja, index) => (
        <div key={index} className="bg-white border-2 border-red-300 rounded-lg p-4 space-y-4 shadow-sm">
          {/* Header de restricción */}
          <div className="flex items-center justify-between pb-3 border-b-2 border-red-200">
            <div className="flex items-center gap-2">
              <span className="text-2xl">🚫</span>
              <span className="text-base font-bold text-red-700">
                Restricción {index + 1}
              </span>
            </div>
            <button
              type="button"
              className="p-2 text-red-600 hover:bg-red-100 rounded-lg transition-colors"
              onClick={() => eliminarFranja(index)}
              title="Eliminar restricción"
            >
              <Trash2 size={18} />
            </button>
          </div>

          {/* Paso 1: Selector de días */}
          <div>
            <label className="text-sm font-bold text-gray-800 mb-3 block flex items-center gap-2">
              <span className="bg-red-500 text-white w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold">1</span>
              Seleccioná el/los día(s) de restricción:
            </label>
            <div className="flex flex-wrap gap-2">
              {DIAS.map(dia => (
                <button
                  key={dia.value}
                  type="button"
                  onClick={() => toggleDia(index, dia.value)}
                  className={`px-4 py-2.5 rounded-lg text-sm font-bold transition-all ${
                    franja.dias.includes(dia.value)
                      ? 'bg-red-500 text-white shadow-md scale-105'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200 border-2 border-gray-300'
                  }`}
                >
                  {dia.label}
                </button>
              ))}
            </div>
            {franja.dias.length === 0 && (
              <p className="text-xs text-red-600 mt-2 font-medium">
                ⚠️ Seleccioná al menos un día
              </p>
            )}
          </div>

          {/* Paso 2: Selectores de horario */}
          <div>
            <label className="text-sm font-bold text-gray-800 mb-3 block flex items-center gap-2">
              <span className="bg-red-500 text-white w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold">2</span>
              Horarios que NO puedes jugar este/estos día(s):
            </label>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-xs font-bold text-gray-700 mb-2 block">
                  Desde:
                </label>
                <select
                  value={franja.horaInicio}
                  onChange={(e) => cambiarHoraInicio(index, e.target.value)}
                  className="w-full px-4 py-3 bg-white border-2 border-gray-300 rounded-lg text-gray-900 font-medium focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500"
                >
                  <option value="" className="text-gray-500">Seleccionar hora</option>
                  {horariosParaMostrar.map(hora => (
                    <option key={hora} value={hora} className="text-gray-900">
                      {hora}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="text-xs font-bold text-gray-700 mb-2 block">
                  Hasta:
                </label>
                <select
                  value={franja.horaFin}
                  onChange={(e) => cambiarHoraFin(index, e.target.value)}
                  className="w-full px-4 py-3 bg-white border-2 border-gray-300 rounded-lg text-gray-900 font-medium focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500 disabled:bg-gray-100 disabled:text-gray-400"
                  disabled={!franja.horaInicio}
                >
                  <option value="" className="text-gray-500">Seleccionar hora</option>
                  {getHorariosFinValidos(franja.horaInicio).map(hora => (
                    <option key={hora} value={hora} className="text-gray-900">
                      {hora}
                    </option>
                  ))}
                </select>
                {!franja.horaInicio && (
                  <p className="text-xs text-red-600 mt-2 font-medium">
                    ⚠️ Primero seleccioná hora de inicio
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Resumen de la restricción */}
          {franja.dias.length > 0 && franja.horaInicio && franja.horaFin && (
            <div className="bg-red-100 border-2 border-red-300 rounded-lg p-3">
              <p className="text-sm text-red-800 font-bold">
                ❌ NO disponible:
              </p>
              <p className="text-sm text-red-700 mt-1">
                <strong>{franja.dias.map(d => DIAS.find(dia => dia.value === d)?.label).join(', ')}</strong> de <strong>{franja.horaInicio}</strong> a <strong>{franja.horaFin}</strong>
              </p>
            </div>
          )}
        </div>
      ))}

      {/* Botón agregar restricción */}
      {value.length < 3 && (
        <button
          type="button"
          className="w-full py-3 px-4 bg-red-500 hover:bg-red-600 text-white border-2 border-red-600 rounded-lg transition-colors text-sm font-bold flex items-center justify-center gap-2 shadow-md"
          onClick={agregarFranja}
        >
          <Plus size={20} />
          Agregar otra restricción horaria
        </button>
      )}

      {/* Nota informativa final */}
      {value.length > 0 && (
        <div className="bg-blue-50 border-2 border-blue-300 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <span className="text-2xl flex-shrink-0">💡</span>
            <div>
              <p className="text-sm text-blue-900 font-bold mb-1">
                Recuerda:
              </p>
              <p className="text-xs text-blue-800">
                Solo especificaste horarios que <strong>NO puedes jugar</strong>. 
                El resto del tiempo (dentro de los horarios del torneo) estarás <strong>disponible automáticamente</strong>.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
