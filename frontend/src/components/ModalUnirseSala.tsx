import { useState } from 'react';
import { X, LogIn, AlertCircle } from 'lucide-react';
import { motion } from 'framer-motion';
import Modal from './Modal';
import Input from './Input';
import Button from './Button';
import { useSalas } from '../context/SalasContext';

interface ModalUnirseSalaProps {
  isOpen: boolean;
  onClose: () => void;
  onUnido?: (salaId: string) => void;
}

export default function ModalUnirseSala({ isOpen, onClose, onUnido }: ModalUnirseSalaProps) {
  const { unirseASala } = useSalas();
  const [codigo, setCodigo] = useState('');
  const [error, setError] = useState('');
  const [validando, setValidando] = useState(false);

  const handleCodigoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value.toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 6);
    setCodigo(value);
    setError('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    if (codigo.length !== 6) {
      setError('El código debe tener 6 caracteres');
      return;
    }

    setValidando(true);

    try {
      // Unirse a la sala usando el servicio
      await unirseASala(codigo);
      
      if (onUnido) {
        onUnido(codigo);
      }
      
      setCodigo('');
      onClose();
    } catch (err: any) {
      setError(err.message || 'Error al unirse a la sala');
    } finally {
      setValidando(false);
    }
  };

  const handleCerrar = () => {
    setCodigo('');
    setError('');
    onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={handleCerrar}>
      <div className="bg-cardBg rounded-2xl p-8 w-full max-w-md border border-cardBorder">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-textPrimary">Unirse a Sala</h2>
          <button
            onClick={handleCerrar}
            className="text-textSecondary hover:text-textPrimary transition-colors"
          >
            <X size={24} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-textSecondary text-sm font-medium mb-3">
              Código de Invitación
            </label>
            <Input
              value={codigo}
              onChange={handleCodigoChange}
              placeholder="ABC123"
              className="text-center text-3xl font-bold tracking-widest uppercase"
              maxLength={6}
              autoFocus
            />
            <p className="text-textSecondary text-xs mt-2 text-center">
              Ingresa el código de 6 caracteres
            </p>
          </div>

          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-red-500/10 border border-red-500/50 rounded-xl p-4 flex items-start gap-3"
            >
              <AlertCircle size={20} className="text-red-500 flex-shrink-0 mt-0.5" />
              <p className="text-red-500 text-sm">{error}</p>
            </motion.div>
          )}

          <div className="bg-primary/10 border border-primary/30 rounded-xl p-4">
            <p className="text-textSecondary text-sm">
              💡 <strong>Tip:</strong> Pídele al creador de la sala que te comparta 
              el código de invitación de 6 caracteres.
            </p>
          </div>

          <div className="flex gap-3">
            <Button 
              type="button" 
              variant="secondary" 
              onClick={handleCerrar} 
              className="flex-1"
            >
              Cancelar
            </Button>
            <Button 
              type="submit" 
              variant="primary" 
              className="flex-1 flex items-center justify-center gap-2"
              disabled={codigo.length !== 6 || validando}
            >
              <LogIn size={18} />
              {validando ? 'Validando...' : 'Unirse'}
            </Button>
          </div>
        </form>
      </div>
    </Modal>
  );
}
