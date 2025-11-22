import { useState, useEffect } from 'react';
import { X, LogIn } from 'lucide-react';
import { motion } from 'framer-motion';
import Modal from './Modal';
import Input from './Input';
import Button from './Button';
import { salaService } from '../services/sala.service';
import { useSalas } from '../context/SalasContext';

interface ModalUnirseSalaProps {
  isOpen: boolean;
  onClose: () => void;
  codigoInicial?: string;
}

export default function ModalUnirseSala({ isOpen, onClose, codigoInicial }: ModalUnirseSalaProps) {
  const { cargarSalas } = useSalas();
  const [codigo, setCodigo] = useState(codigoInicial || '');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  // Actualizar código cuando cambia el inicial
  useEffect(() => {
    if (codigoInicial) {
      setCodigo(codigoInicial);
    }
  }, [codigoInicial]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!codigo.trim()) {
      setError('Por favor ingresa un código');
      return;
    }

    try {
      setLoading(true);
      setError('');
      
      const salaUnida = await salaService.unirseASala(codigo.toUpperCase());
      
      // Recargar salas
      await cargarSalas();
      
      // Mostrar mensaje de éxito más visual
      setCodigo('');
      setError('');
      
      // Cerrar modal y mostrar notificación
      onClose();
      
      // Notificación visual en lugar de alert
      const notification = document.createElement('div');
      notification.className = 'fixed top-4 right-4 bg-secondary text-white px-6 py-4 rounded-xl shadow-2xl z-50 flex items-center gap-3 animate-slide-in';
      notification.innerHTML = `
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
        </svg>
        <div>
          <p class="font-bold">¡Unido exitosamente!</p>
          <p class="text-sm opacity-90">${salaUnida.nombre}</p>
        </div>
      `;
      document.body.appendChild(notification);
      setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => notification.remove(), 300);
      }, 3000);
    } catch (error: any) {
      setError(error.message || 'Error al unirse a la sala');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setCodigo('');
    setError('');
    onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={handleClose}>
      <div className="bg-cardBg rounded-2xl md:rounded-3xl p-4 md:p-6 w-full max-w-md border border-cardBorder shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between mb-4 md:mb-6">
          <div className="flex items-center gap-2 md:gap-3">
            <div className="bg-gradient-to-br from-primary to-secondary rounded-lg p-2 md:p-2.5">
              <LogIn size={20} className="text-white md:w-6 md:h-6" />
            </div>
            <h2 className="text-lg md:text-2xl font-bold text-textPrimary">
              Unirse a Sala
            </h2>
          </div>
          <motion.button
            onClick={handleClose}
            whileHover={{ scale: 1.1, rotate: 90 }}
            whileTap={{ scale: 0.9 }}
            className="text-textSecondary hover:text-textPrimary transition-colors bg-cardBorder rounded-full p-2"
          >
            <X size={20} className="md:w-6 md:h-6" />
          </motion.button>
        </div>

        {/* Descripción */}
        <p className="text-textSecondary text-xs md:text-sm mb-4 md:mb-6">
          Ingresa el código de invitación que te compartieron para unirte a la sala
        </p>

        {/* Formulario */}
        <form onSubmit={handleSubmit} className="space-y-4 md:space-y-5">
          <div>
            <label className="block text-textPrimary text-xs md:text-sm font-bold mb-2">
              Código de Invitación
            </label>
            <Input
              type="text"
              value={codigo}
              onChange={(e) => {
                setCodigo(e.target.value.toUpperCase());
                setError('');
              }}
              placeholder="Ej: ABC123"
              maxLength={6}
              className="text-center text-lg md:text-xl font-bold tracking-widest uppercase"
              autoFocus
            />
            <p className="text-textSecondary text-[10px] md:text-xs mt-1.5 md:mt-2">
              El código tiene 6 caracteres
            </p>
          </div>

          {/* Error */}
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-red-500/10 border border-red-500/50 rounded-lg p-3 text-red-500 text-xs md:text-sm"
            >
              {error}
            </motion.div>
          )}

          {/* Botones */}
          <div className="flex gap-2 md:gap-3 pt-2">
            <Button
              type="button"
              variant="ghost"
              onClick={handleClose}
              className="flex-1 text-xs md:text-sm py-2.5 md:py-3"
            >
              Cancelar
            </Button>
            <Button
              type="submit"
              variant="primary"
              disabled={loading || !codigo.trim()}
              className="flex-1 text-xs md:text-sm py-2.5 md:py-3"
            >
              {loading ? 'Uniéndose...' : 'Unirse'}
            </Button>
          </div>
        </form>

        {/* Ayuda */}
        <div className="mt-4 md:mt-6 pt-4 md:pt-6 border-t border-cardBorder">
          <p className="text-textSecondary text-[10px] md:text-xs text-center">
            💡 El creador de la sala debe compartirte el código de 6 caracteres
          </p>
        </div>
      </div>
    </Modal>
  );
}
