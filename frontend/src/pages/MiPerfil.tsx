import { motion } from 'framer-motion';
import { Mail, Calendar, Trophy, Target, TrendingUp } from 'lucide-react';
import Card from '../components/Card';
import { useAuth } from '../context/AuthContext';

export default function MiPerfil() {
  const { usuario } = useAuth();

  if (!usuario) return null;

  const nombreCompleto = `${usuario.nombre} ${usuario.apellido}`;
  const iniciales = `${usuario.nombre[0]}${usuario.apellido[0]}`.toUpperCase();

  return (
    <div className="space-y-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="relative"
      >
        <div className="flex items-center gap-2 md:gap-3 mb-1 md:mb-2">
          <div className="h-0.5 md:h-1 w-8 md:w-12 bg-gradient-to-r from-primary to-secondary rounded-full" />
          <h1 className="text-2xl md:text-5xl font-black text-textPrimary tracking-tight">
            Mi Perfil
          </h1>
        </div>
        <p className="text-textSecondary text-xs md:text-base ml-10 md:ml-15">
          Información personal y estadísticas
        </p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-3 md:gap-6">
        {/* Información Personal */}
        <Card className="lg:col-span-1">
          <div className="text-center">
            <div className="w-24 h-24 md:w-32 md:h-32 rounded-full bg-gradient-to-br from-primary to-blue-600 flex items-center justify-center text-white text-4xl md:text-5xl font-black mx-auto mb-3 md:mb-4">
              {iniciales}
            </div>
            <h2 className="text-xl md:text-2xl font-bold text-textPrimary mb-1">{nombreCompleto}</h2>
            <p className="text-textSecondary text-sm md:text-base mb-1 md:mb-2">@{usuario.nombre_usuario}</p>
            <p className="text-textSecondary text-xs md:text-sm mb-3 md:mb-4 truncate px-4">{usuario.email}</p>
            <span className="inline-block px-3 md:px-4 py-1.5 md:py-2 rounded-full bg-primary/10 text-primary font-bold text-xs md:text-sm">
              Rating: {usuario.rating}
            </span>
          </div>

          <div className="mt-4 md:mt-6 space-y-2 md:space-y-3">
            <div className="flex items-center gap-2 md:gap-3 text-textSecondary">
              <Mail size={16} className="md:w-5 md:h-5 flex-shrink-0" />
              <span className="text-xs md:text-sm truncate">{usuario.email}</span>
            </div>
            {usuario.ciudad && usuario.pais && (
              <div className="flex items-center gap-2 md:gap-3 text-textSecondary">
                <Calendar size={16} className="md:w-5 md:h-5 flex-shrink-0" />
                <span className="text-xs md:text-sm">{usuario.ciudad}, {usuario.pais}</span>
              </div>
            )}
          </div>
        </Card>

        {/* Estadísticas */}
        <Card className="lg:col-span-2">
          <h3 className="text-lg md:text-2xl font-bold text-textPrimary mb-4 md:mb-6">Estadísticas</h3>
          
          <div className="grid grid-cols-3 gap-2 md:gap-4">
            <div className="bg-background rounded-lg md:rounded-xl p-2 md:p-4 text-center">
              <Trophy size={24} className="text-primary mx-auto mb-1 md:mb-2 md:w-8 md:h-8" />
              <p className="text-xl md:text-3xl font-black text-textPrimary">{usuario.partidos_jugados}</p>
              <p className="text-textSecondary text-[10px] md:text-sm">Partidos</p>
            </div>
            <div className="bg-background rounded-lg md:rounded-xl p-2 md:p-4 text-center">
              <Target size={24} className="text-secondary mx-auto mb-1 md:mb-2 md:w-8 md:h-8" />
              <p className="text-xl md:text-3xl font-black text-textPrimary">{usuario.rating}</p>
              <p className="text-textSecondary text-[10px] md:text-sm">Rating</p>
            </div>
            <div className="bg-background rounded-lg md:rounded-xl p-2 md:p-4 text-center">
              <TrendingUp size={24} className="text-accent mx-auto mb-1 md:mb-2 md:w-8 md:h-8" />
              <p className="text-xl md:text-3xl font-black text-textPrimary">
                {usuario.sexo === 'M' ? '♂' : '♀'}
              </p>
              <p className="text-textSecondary text-[10px] md:text-sm">Género</p>
            </div>
          </div>

          <div className="mt-4 md:mt-6 bg-background rounded-lg md:rounded-xl p-3 md:p-6">
            <h4 className="text-base md:text-lg font-bold text-textPrimary mb-3 md:mb-4">Información</h4>
            <div className="space-y-2 md:space-y-3">
              <div className="flex justify-between gap-2">
                <span className="text-textSecondary text-xs md:text-sm">Usuario:</span>
                <span className="text-textPrimary font-bold text-xs md:text-base truncate">{usuario.nombre_usuario}</span>
              </div>
              <div className="flex justify-between gap-2">
                <span className="text-textSecondary text-xs md:text-sm">Email:</span>
                <span className="text-textPrimary font-bold text-xs md:text-base truncate">{usuario.email}</span>
              </div>
              <div className="flex justify-between gap-2">
                <span className="text-textSecondary text-xs md:text-sm">Rating:</span>
                <span className="text-primary font-bold text-lg md:text-xl">{usuario.rating}</span>
              </div>
              <div className="flex justify-between gap-2">
                <span className="text-textSecondary text-xs md:text-sm">Partidos:</span>
                <span className="text-textPrimary font-bold text-xs md:text-base">{usuario.partidos_jugados}</span>
              </div>
              {usuario.id_categoria && (
                <div className="flex justify-between gap-2">
                  <span className="text-textSecondary text-xs md:text-sm">Categoría ID:</span>
                  <span className="text-textPrimary font-bold text-xs md:text-base">{usuario.id_categoria}</span>
                </div>
              )}
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
