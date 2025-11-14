import { useState } from 'react';
import { X } from 'lucide-react';
import Modal from './Modal';
import Input from './Input';
import Button from './Button';
import { useSalas } from '../context/SalasContext';
import { useAuth } from '../context/AuthContext';

interface ModalCrearSalaProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function ModalCrearSala({ isOpen, onClose }: ModalCrearSalaProps) {
  const { addSala } = useSalas();
  const { usuario } = useAuth();
  const [formData, setFormData] = useState({
    nombre: '',
    fecha: new Date().toISOString().split('T')[0],
    jugador1A: '',
    jugador2A: '',
    jugador1B: '',
    jugador2B: '',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.nombre || !formData.jugador1A || !formData.jugador2A || 
        !formData.jugador1B || !formData.jugador2B) {
      alert('Por favor completa todos los campos');
      return;
    }

    addSala({
      nombre: formData.nombre,
      fecha: formData.fecha,
      estado: 'programada',
      creadoPor: usuario?.id || '',
      estadoConfirmacion: 'pendiente',
      resultadoFinal: false,
      equipoA: {
        jugador1: { id: crypto.randomUUID(), nombre: formData.jugador1A },
        jugador2: { id: crypto.randomUUID(), nombre: formData.jugador2A },
        puntos: 0,
        confirmado: false
      },
      equipoB: {
        jugador1: { id: crypto.randomUUID(), nombre: formData.jugador1B },
        jugador2: { id: crypto.randomUUID(), nombre: formData.jugador2B },
        puntos: 0,
        confirmado: false
      }
    });

    setFormData({
      nombre: '',
      fecha: new Date().toISOString().split('T')[0],
      jugador1A: '',
      jugador2A: '',
      jugador1B: '',
      jugador2B: '',
    });
    onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose}>
      <div className="bg-cardBg rounded-2xl p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-textPrimary">Nueva Sala</h2>
          <button
            onClick={onClose}
            className="text-textSecondary hover:text-textPrimary transition-colors"
          >
            <X size={24} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-textSecondary text-sm mb-2">Nombre de la Sala</label>
            <Input
              value={formData.nombre}
              onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
              placeholder="Ej: Final del Torneo"
            />
          </div>

          <div>
            <label className="block text-textSecondary text-sm mb-2">Fecha</label>
            <Input
              type="date"
              value={formData.fecha}
              onChange={(e) => setFormData({ ...formData, fecha: e.target.value })}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-primary">Equipo A</h3>
              <div>
                <label className="block text-textSecondary text-sm mb-2">Jugador 1</label>
                <Input
                  value={formData.jugador1A}
                  onChange={(e) => setFormData({ ...formData, jugador1A: e.target.value })}
                  placeholder="Nombre del jugador"
                />
              </div>
              <div>
                <label className="block text-textSecondary text-sm mb-2">Jugador 2</label>
                <Input
                  value={formData.jugador2A}
                  onChange={(e) => setFormData({ ...formData, jugador2A: e.target.value })}
                  placeholder="Nombre del jugador"
                />
              </div>
            </div>

            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-secondary">Equipo B</h3>
              <div>
                <label className="block text-textSecondary text-sm mb-2">Jugador 1</label>
                <Input
                  value={formData.jugador1B}
                  onChange={(e) => setFormData({ ...formData, jugador1B: e.target.value })}
                  placeholder="Nombre del jugador"
                />
              </div>
              <div>
                <label className="block text-textSecondary text-sm mb-2">Jugador 2</label>
                <Input
                  value={formData.jugador2B}
                  onChange={(e) => setFormData({ ...formData, jugador2B: e.target.value })}
                  placeholder="Nombre del jugador"
                />
              </div>
            </div>
          </div>

          <div className="flex gap-3 pt-4">
            <Button type="button" variant="secondary" onClick={onClose} className="flex-1">
              Cancelar
            </Button>
            <Button type="submit" variant="primary" className="flex-1">
              Crear Sala
            </Button>
          </div>
        </form>
      </div>
    </Modal>
  );
}
