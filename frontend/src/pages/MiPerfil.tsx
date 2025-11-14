import { motion } from 'framer-motion';
import { Mail, Calendar, Trophy, Target, TrendingUp } from 'lucide-react';
import Card from '../components/Card';
import { useAuth } from '../context/AuthContext';

export default function MiPerfil() {
  const { usuario } = useAuth();

  if (!usuario) return null;

  return (
    <div className="space-y-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -30 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative"
      >
        <div className="flex items-center gap-3 mb-2">
          <div className="h-1 w-12 bg-gradient-to-r from-primary to-secondary rounded-full" />
          <h1 className="text-5xl font-black text-textPrimary tracking-tight">
            Mi Perfil
          </h1>
        </div>
        <p className="text-textSecondary text-base ml-15">
          Información personal y estadísticas
        </p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Información Personal */}
        <Card className="lg:col-span-1">
          <div className="text-center">
            <div className="w-32 h-32 rounded-full bg-gradient-to-br from-primary to-blue-600 flex items-center justify-center text-white text-5xl font-black mx-auto mb-4">
              {usuario.nombre.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)}
            </div>
            <h2 className="text-2xl font-bold text-textPrimary mb-1">{usuario.nombre}</h2>
            <p className="text-textSecondary mb-4">{usuario.email}</p>
            <span className="inline-block px-4 py-2 rounded-full bg-primary/10 text-primary font-bold text-sm">
              {usuario.rol}
            </span>
          </div>

          <div className="mt-6 space-y-3">
            <div className="flex items-center gap-3 text-textSecondary">
              <Mail size={20} />
              <span className="text-sm">{usuario.email}</span>
            </div>
            <div className="flex items-center gap-3 text-textSecondary">
              <Calendar size={20} />
              <span className="text-sm">
                Miembro desde {new Date(usuario.createdAt).toLocaleDateString('es-ES')}
              </span>
            </div>
          </div>
        </Card>

        {/* Estadísticas */}
        <Card className="lg:col-span-2">
          <h3 className="text-2xl font-bold text-textPrimary mb-6">Estadísticas</h3>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-background rounded-xl p-4 text-center">
              <Trophy size={32} className="text-primary mx-auto mb-2" />
              <p className="text-3xl font-black text-textPrimary">{usuario.estadisticas.partidosJugados}</p>
              <p className="text-textSecondary text-sm">Partidos</p>
            </div>
            <div className="bg-background rounded-xl p-4 text-center">
              <Target size={32} className="text-secondary mx-auto mb-2" />
              <p className="text-3xl font-black text-textPrimary">{usuario.estadisticas.partidosGanados}</p>
              <p className="text-textSecondary text-sm">Ganados</p>
            </div>
            <div className="bg-background rounded-xl p-4 text-center">
              <TrendingUp size={32} className="text-accent mx-auto mb-2" />
              <p className="text-3xl font-black text-textPrimary">
                {usuario.estadisticas.partidosJugados > 0 
                  ? Math.round((usuario.estadisticas.partidosGanados / usuario.estadisticas.partidosJugados) * 100)
                  : 0}%
              </p>
              <p className="text-textSecondary text-sm">Victoria</p>
            </div>
            <div className="bg-background rounded-xl p-4 text-center">
              <Trophy size={32} className="text-purple-400 mx-auto mb-2" />
              <p className="text-3xl font-black text-textPrimary">{usuario.estadisticas.torneosParticipados}</p>
              <p className="text-textSecondary text-sm">Torneos</p>
            </div>
          </div>

          <div className="mt-6 bg-background rounded-xl p-6">
            <h4 className="text-lg font-bold text-textPrimary mb-4">Logros</h4>
            <div className="grid grid-cols-2 gap-4">
              {usuario.estadisticas.partidosJugados >= 10 && (
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center">
                    <Trophy className="text-primary" size={24} />
                  </div>
                  <div>
                    <p className="text-textPrimary font-bold">Veterano</p>
                    <p className="text-textSecondary text-xs">10+ partidos</p>
                  </div>
                </div>
              )}
              {usuario.estadisticas.partidosGanados >= 5 && (
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-full bg-secondary/20 flex items-center justify-center">
                    <Target className="text-secondary" size={24} />
                  </div>
                  <div>
                    <p className="text-textPrimary font-bold">Ganador</p>
                    <p className="text-textSecondary text-xs">5+ victorias</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
