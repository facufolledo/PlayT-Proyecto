import { useState } from 'react';
import { X, DollarSign, Copy, CheckCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import Button from './Button';
import Card from './Card';

interface ModalPagoInscripcionProps {
  isOpen: boolean;
  onClose: () => void;
  pagoInfo: {
    monto: number;
    alias_cbu_cvu: string;
    titular: string;
    banco: string;
  };
}

export default function ModalPagoInscripcion({
  isOpen,
  onClose,
  pagoInfo
}: ModalPagoInscripcionProps) {
  const [copiado, setCopiado] = useState(false);

  const copiarAlias = () => {
    navigator.clipboard.writeText(pagoInfo.alias_cbu_cvu);
    setCopiado(true);
    setTimeout(() => setCopiado(false), 2000);
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50"
            onClick={onClose}
          />
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4"
          >
            <Card className="w-full max-w-md relative">
              <button
                onClick={onClose}
                className="absolute top-4 right-4 text-textSecondary hover:text-textPrimary"
              >
                <X size={24} />
              </button>

              <div className="text-center mb-6">
                <div className="w-16 h-16 bg-accent/10 rounded-full flex items-center justify-center mx-auto mb-4">
                  <DollarSign size={32} className="text-accent" />
                </div>
                <h2 className="text-2xl font-bold text-textPrimary mb-2">
                  Completá tu inscripción
                </h2>
                <p className="text-textSecondary">
                  Realizá la transferencia con los siguientes datos
                </p>
              </div>

              <div className="space-y-4 mb-6">
                <div className="bg-cardHover rounded-lg p-4">
                  <div className="flex justify-between items-center mb-3">
                    <span className="text-textSecondary text-sm">Monto a transferir</span>
                    <span className="text-2xl font-bold text-accent">
                      ${pagoInfo.monto.toLocaleString('es-AR')}
                    </span>
                  </div>
                  
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-textSecondary">Alias/CBU/CVU:</span>
                      <div className="flex items-center gap-2">
                        <span className="text-textPrimary font-mono">{pagoInfo.alias_cbu_cvu}</span>
                        <button
                          onClick={copiarAlias}
                          className="text-accent hover:text-accent/80 transition-colors"
                          title="Copiar"
                        >
                          {copiado ? <CheckCircle size={16} /> : <Copy size={16} />}
                        </button>
                      </div>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-textSecondary">Titular:</span>
                      <span className="text-textPrimary">{pagoInfo.titular}</span>
                    </div>
                    {pagoInfo.banco && (
                      <div className="flex justify-between">
                        <span className="text-textSecondary">Banco:</span>
                        <span className="text-textPrimary">{pagoInfo.banco}</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Instrucciones */}
                <div className="bg-cardHover rounded-lg p-4">
                  <h3 className="font-semibold text-textPrimary mb-2 text-sm">
                    Cómo pagar:
                  </h3>
                  <ol className="text-xs text-textSecondary space-y-1 list-decimal list-inside">
                    <li>Abrí tu app de banco o Mercado Pago</li>
                    <li>Seleccioná "Transferir" o "Enviar dinero"</li>
                    <li>Ingresá el alias: <strong className="text-textPrimary">{pagoInfo.alias_cbu_cvu}</strong></li>
                    <li>Transferí <strong className="text-accent">${pagoInfo.monto.toLocaleString('es-AR')}</strong></li>
                    <li>Esperá la confirmación del organizador</li>
                  </ol>
                </div>

                {/* Información adicional */}
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                  <p className="text-xs text-blue-800">
                    <strong>Importante:</strong> Tu inscripción quedará pendiente hasta que el organizador verifique el pago. Una vez confirmado, recibirás una notificación.
                  </p>
                </div>
              </div>

              <Button
                variant="ghost"
                onClick={onClose}
                className="w-full"
              >
                Cerrar
              </Button>
            </Card>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
