import { motion } from 'framer-motion';
import { X, Clock, Calendar } from 'lucide-react';
import Button from './Button';

interface ModalHorariosParejaProps {
  isOpen: boolean;
  onClose: () => void;
  pareja: {
    nombre: string;
    disponibilidad_horaria?: any;
  };
}

export default function ModalHorariosPareja({
  isOpen,
  onClose,
  pareja,
}: ModalHorariosParejaProps) {
  if (!isOpen) return null;

  // Parsear disponibilidad horaria
  let franjas: any[] = [];
  try {
    if (pareja.disponibilidad_horaria) {
      const disponibilidad = typeof pareja.disponibilidad_horaria === 'string'
        ? JSON.parse(pareja.disponibilidad_horaria)
        : pareja.disponibilidad_horaria;
      franjas = disponibilidad?.franjas || [];
    }
  } catch (error) {
    console.error('Error parseando disponibilidad horaria:', error);
  }

  // Mapeo de días en español
  const diasMap: Record<string, string> = {
    'lunes': 'Lunes',
    'martes': 'Martes',
    'miercoles': 'Miércoles',
    'miércoles': 'Miércoles',
    'jueves': 'Jueves',
    'viernes': 'Viernes',
    'sabado': 'Sábado',
    'sábado': 'Sábado',
    'domingo': 'Domingo',
  };

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="bg-card rounded-xl max-w-md w-full max-h-[90vh] overflow-y-auto"
      >
        {/* Header */}
        <div className="sticky top-0 bg-card border-b border-cardBorder p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-primary/10 p-2 rounded-lg">
              <Clock size={20} className="text-primary" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-textPrimary">
                Horarios Disponibles
              </h3>
              <p className="text-xs text-textSecondary">{pareja.nombre}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-textSecondary hover:text-textPrimary transition-colors p-1"
          >
            <X size={20} />
          </button>
        </div>

        {/* Content */}
        <div className="p-4">
          {franjas.length === 0 ? (
            <div className="text-center py-8">
              <Calendar size={48} className="mx-auto text-textSecondary mb-3" />
              <p className="text-textSecondary text-sm">
                Esta pareja no tiene restricciones horarias
              </p>
              <p className="text-textSecondary text-xs mt-2">
                Pueden jugar en cualquier horario del torneo
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              <p className="text-xs text-textSecondary mb-3">
                Esta pareja solo puede jugar en los siguientes horarios:
              </p>
              {franjas.map((franja: any, index: number) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="p-3 bg-background rounded-lg border border-cardBorder"
                >
                  {/* Días */}
                  <div className="flex items-center gap-2 mb-2">
                    <Calendar size={14} className="text-accent flex-shrink-0" />
                    <div className="flex flex-wrap gap-1">
                      {franja.dias?.map((dia: string, idx: number) => (
                        <span
                          key={idx}
                          className="px-2 py-0.5 bg-accent/10 text-accent rounded text-xs font-bold"
                        >
                          {diasMap[dia.toLowerCase()] || dia}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Horario */}
                  <div className="flex items-center gap-2">
                    <Clock size={14} className="text-primary flex-shrink-0" />
                    <span className="text-sm text-textPrimary font-medium">
                      {franja.horaInicio} - {franja.horaFin}
                    </span>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="sticky bottom-0 bg-card border-t border-cardBorder p-4">
          <Button variant="ghost" onClick={onClose} className="w-full">
            Cerrar
          </Button>
        </div>
      </motion.div>
    </div>
  );
}
