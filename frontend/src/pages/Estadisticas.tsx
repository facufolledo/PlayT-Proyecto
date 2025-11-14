import { motion } from 'framer-motion';
import Card from '../components/Card';

export default function Estadisticas() {
  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <h1 className="text-4xl font-bold text-textPrimary mb-2">Estadísticas</h1>
        <p className="text-textSecondary">Análisis detallado de rendimiento y métricas</p>
      </motion.div>

      <Card>
        <div className="text-center py-12 text-textSecondary">
          <p className="text-lg mb-4">No hay datos suficientes</p>
          <p className="text-sm">Las estadísticas aparecerán cuando tengas partidos registrados</p>
        </div>
      </Card>
    </div>
  );
}
