import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Bug, ChevronDown, ChevronUp } from 'lucide-react';

interface SalasDebugProps {
  salas: any[];
  usuario: any;
}

export const SalasDebug: React.FC<SalasDebugProps> = ({ salas, usuario }) => {
  const [expanded, setExpanded] = useState(false);

  if (process.env.NODE_ENV === 'production') {
    return null; // No mostrar en producción
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="mb-4 bg-yellow-50 border border-yellow-200 rounded-lg overflow-hidden"
    >
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full px-4 py-2 bg-yellow-100 hover:bg-yellow-200 transition-colors flex items-center justify-between text-sm font-medium text-yellow-800"
      >
        <div className="flex items-center gap-2">
          <Bug size={16} />
          <span>Debug Info - Salas ({salas.length})</span>
        </div>
        {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
      </button>
      
      {expanded && (
        <div className="p-4 bg-yellow-50 border-t border-yellow-200">
          <div className="mb-4">
            <h4 className="font-bold text-yellow-800 mb-2">Usuario Actual:</h4>
            <pre className="text-xs bg-white p-2 rounded border overflow-x-auto">
              {JSON.stringify({
                id_usuario: usuario?.id_usuario,
                nombre: usuario?.nombre,
                apellido: usuario?.apellido
              }, null, 2)}
            </pre>
          </div>
          
          <div>
            <h4 className="font-bold text-yellow-800 mb-2">Salas Raw Data:</h4>
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {salas.map((sala, index) => (
                <div key={index} className="bg-white p-2 rounded border">
                  <div className="text-xs font-mono">
                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <strong>ID:</strong> {sala.id}<br/>
                        <strong>Nombre:</strong> {sala.nombre || 'Sin nombre'}<br/>
                        <strong>Estado:</strong> <span className="bg-blue-100 px-1 rounded">{sala.estado}</span><br/>
                        <strong>Creador ID:</strong> {sala.creador_id}<br/>
                        <strong>Fecha:</strong> {sala.fecha_creacion}
                      </div>
                      <div>
                        <strong>Jugadores ({sala.jugadores?.length || 0}):</strong><br/>
                        {sala.jugadores?.map((j: any, i: number) => (
                          <div key={i} className="ml-2 text-[10px]">
                            • {j.nombre} (ID: {j.id})
                          </div>
                        )) || <span className="text-gray-500">Sin jugadores</span>}
                      </div>
                    </div>
                    
                    <div className="mt-2 pt-2 border-t">
                      <strong>¿Es mi sala?</strong> {
                        sala.jugadores?.some((j: any) => j.id === usuario?.id_usuario?.toString()) ? 
                        '✅ SÍ' : '❌ NO'
                      }<br/>
                      <strong>¿Soy organizador?</strong> {
                        sala.creador_id === usuario?.id_usuario?.toString() || sala.creador_id === usuario?.id_usuario ? 
                        '✅ SÍ' : '❌ NO'
                      }
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </motion.div>
  );
};