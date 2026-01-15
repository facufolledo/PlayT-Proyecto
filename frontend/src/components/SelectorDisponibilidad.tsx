import { Clock, Trash2, Plus } from 'lucide-react';

interface FranjaHoraria {
  dias: string[];
  horaInicio: string;
  horaFin: string;
}

interface SelectorDisponibilidadProps {
  value: FranjaHoraria[];
  onChange: (disponibilidad: FranjaHoraria[]) => void;
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
    if (value.length < 2) {
      onChange([...value, { dias: [], horaInicio: '', horaFin: '' }]);
    }
  };

  const eliminarFranja = (index: number) => {
    onChange(value.filter((_, i) => i !== index));
  };

  const toggleDia = (franjaIndex: number, dia: string) => {
    const nuevaDisponibilidad = [...value];
    const franja = nuevaDisponibilidad[franjaIndex];
    
    if (franja.dias.includes(dia)) {
      franja.dias = franja.dias.filter(d => d !== dia);
    } else {
      franja.dias = [...franja.dias, dia];
    }
    
    onChange(nuevaDisponibilidad);
  };

  const cambiarHoraInicio = (franjaIndex: number, hora: string) => {
    const nuevaDisponibilidad = [...value];
    nuevaDisponibilidad[franjaIndex].horaInicio = hora;
    // Si la hora de fin es anterior a la nueva hora de inicio, resetearla
    if (nuevaDisponibilidad[franjaIndex].horaFin && nuevaDisponibilidad[franjaIndex].horaFin <= hora) {
      nuevaDisponibilidad[franjaIndex].horaFin = '';
    }
    onChange(nuevaDisponibilidad);
  };

  const cambiarHoraFin = (franjaIndex: number, hora: string) => {
    const nuevaDisponibilidad = [...value];
    nuevaDisponibilidad[franjaIndex].horaFin = hora;
    onChange(nuevaDisponibilidad);
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
          Disponibilidad horaria (máximo 2 franjas)
        </label>
      </div>

      {value.map((franja, index) => (
        <div key={index} className="bg-cardHover rounded-lg p-4 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-textPrimary">
              Franja {index + 1}
            </span>
            <button
              type="button"
              className="p-1 text-red-500 hover:bg-red-50 rounded transition-colors"
              onClick={() => eliminarFranja(index)}
              title="Eliminar franja"
            >
              <Trash2 size={16} />
            </button>
          </div>

          {/* Selector de días */}
          <div>
            <label className="text-xs text-textSecondary mb-2 block">
              Días disponibles:
            </label>
            <div className="flex flex-wrap gap-2">
              {DIAS.map(dia => (
                <button
                  key={dia.value}
                  type="button"
                  onClick={() => toggleDia(index, dia.value)}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                    franja.dias.includes(dia.value)
                      ? 'bg-accent text-white'
                      : 'bg-card text-textSecondary hover:bg-cardBorder'
                  }`}
                >
                  {dia.label}
                </button>
              ))}
            </div>
          </div>

          {/* Selector de horario */}
          <div>
            <label className="text-xs text-textSecondary mb-2 block">
              Horario:
            </label>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs text-textSecondary mb-1 block">
                  Desde:
                </label>
                <select
                  value={franja.horaInicio}
                  onChange={(e) => cambiarHoraInicio(index, e.target.value)}
                  className="w-full px-3 py-2 bg-card border border-cardBorder rounded-lg text-textPrimary focus:outline-none focus:ring-2 focus:ring-accent"
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
                <label className="text-xs text-textSecondary mb-1 block">
                  Hasta:
                </label>
                <select
                  value={franja.horaFin}
                  onChange={(e) => cambiarHoraFin(index, e.target.value)}
                  className="w-full px-3 py-2 bg-card border border-cardBorder rounded-lg text-textPrimary focus:outline-none focus:ring-2 focus:ring-accent"
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
                  <p className="text-xs text-textSecondary mt-1">
                    Primero seleccioná hora de inicio
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Resumen de la franja */}
          {franja.dias.length > 0 && franja.horaInicio && franja.horaFin && (
            <div className="text-xs text-textSecondary bg-card rounded p-2">
              <strong>Resumen:</strong> {franja.dias.map(d => DIAS.find(dia => dia.value === d)?.label).join(', ')} de {franja.horaInicio} a {franja.horaFin}
            </div>
          )}
        </div>
      ))}

      {value.length < 2 && (
        <button
          type="button"
          className="w-full py-2.5 px-4 bg-cardHover hover:bg-cardBorder text-textPrimary rounded-lg transition-colors text-sm font-medium flex items-center justify-center gap-2"
          onClick={agregarFranja}
        >
          <Plus size={18} />
          Agregar franja horaria
        </button>
      )}

      {value.length === 0 && (
        <p className="text-xs text-textSecondary italic">
          Agregá al menos una franja horaria para que el organizador pueda coordinar los partidos
        </p>
      )}
    </div>
  );
}
