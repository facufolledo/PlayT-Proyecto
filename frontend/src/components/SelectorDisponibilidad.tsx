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
  const inicio = new Date(fechaInicio);
  const fin = new Date(fechaFin);
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
  fechaFin
}: SelectorDisponibilidadProps) {
  // Calcular días disponibles según las fechas del torneo
  const diasDisponibles = calcularDiasDisponibles(fechaInicio, fechaFin);
  const DIAS = TODOS_LOS_DIAS.filter(dia => diasDisponibles.includes(dia.value));

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
    if (!horaInicio) return HORARIOS_DISPONIBLES;
    return HORARIOS_DISPONIBLES.filter(hora => hora > horaInicio);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium text-textPrimary flex items-center gap-2">
          <Clock size={16} />
          Restricciones horarias (opcional)
        </label>
        <p className="text-xs text-textSecondary">
          Solo especifica horarios que NO puedes jugar
        </p>
      </div>

      {value.length === 0 && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
          <p className="text-sm text-green-700 font-medium">
            ✅ Sin restricciones - Disponible en todos los horarios del torneo
          </p>
          <p className="text-xs text-green-600 mt-1">
            Si tienes horarios específicos que NO puedes jugar, agrégalos abajo
          </p>
        </div>
      )}

      {value.map((franja, index) => (
        <div key={index} className="bg-red-50 border border-red-200 rounded-lg p-4 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-red-700">
              ❌ Restricción {index + 1}
            </span>
            <button
              type="button"
              className="p-1 text-red-500 hover:bg-red-100 rounded transition-colors"
              onClick={() => eliminarFranja(index)}
              title="Eliminar restricción"
            >
              <Trash2 size={16} />
            </button>
          </div>

          {/* Selector de días */}
          <div>
            <label className="text-xs text-red-600 mb-2 block">
              Días que NO puedes jugar:
            </label>
            <div className="flex flex-wrap gap-2">
              {DIAS.map(dia => (
                <button
                  key={dia.value}
                  type="button"
                  onClick={() => toggleDia(index, dia.value)}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                    franja.dias.includes(dia.value)
                      ? 'bg-red-500 text-white'
                      : 'bg-white text-textSecondary hover:bg-red-100 border border-red-200'
                  }`}
                >
                  {dia.label}
                </button>
              ))}
            </div>
          </div>

          {/* Selectores de horario */}
          <div>
            <label className="text-xs text-red-600 mb-2 block">
              Horario que NO puedes jugar:
            </label>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs text-red-600 mb-1 block">
                  Desde:
                </label>
                <select
                  value={franja.horaInicio}
                  onChange={(e) => cambiarHoraInicio(index, e.target.value)}
                  className="w-full px-3 py-2 bg-white border border-red-200 rounded-lg text-textPrimary focus:outline-none focus:ring-2 focus:ring-red-500"
                >
                  <option value="">Seleccionar</option>
                  {HORARIOS_DISPONIBLES.map(hora => (
                    <option key={hora} value={hora}>
                      {hora}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="text-xs text-red-600 mb-1 block">
                  Hasta:
                </label>
                <select
                  value={franja.horaFin}
                  onChange={(e) => cambiarHoraFin(index, e.target.value)}
                  className="w-full px-3 py-2 bg-white border border-red-200 rounded-lg text-textPrimary focus:outline-none focus:ring-2 focus:ring-red-500"
                  disabled={!franja.horaInicio}
                >
                  <option value="">Seleccionar</option>
                  {getHorariosFinValidos(franja.horaInicio).map(hora => (
                    <option key={hora} value={hora}>
                      {hora}
                    </option>
                  ))}
                </select>
                {!franja.horaInicio && (
                  <p className="text-xs text-red-600 mt-1">
                    Primero seleccioná hora de inicio
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Resumen de la restricción */}
          {franja.dias.length > 0 && franja.horaInicio && franja.horaFin && (
            <div className="text-xs text-red-700 bg-red-100 rounded p-2">
              <strong>❌ NO disponible:</strong> {franja.dias.map(d => DIAS.find(dia => dia.value === d)?.label).join(', ')} de {franja.horaInicio} a {franja.horaFin}
            </div>
          )}
        </div>
      ))}

      {value.length < 3 && (
        <button
          type="button"
          className="w-full py-2.5 px-4 bg-red-50 hover:bg-red-100 text-red-700 border border-red-200 rounded-lg transition-colors text-sm font-medium flex items-center justify-center gap-2"
          onClick={agregarFranja}
        >
          <Plus size={18} />
          Agregar restricción horaria
        </button>
      )}

      {value.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
          <p className="text-xs text-blue-700">
            💡 <strong>Recuerda:</strong> Solo especifica horarios que NO puedes jugar. 
            El resto del tiempo (dentro de los horarios del torneo) estarás disponible automáticamente.
          </p>
        </div>
      )}
    </div>
  );
}
