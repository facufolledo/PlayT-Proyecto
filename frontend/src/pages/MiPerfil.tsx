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
              {iniciales}
            </div>
            <h2 className="text-2xl font-bold text-textPrimary mb-1">{nombreCompleto}</h2>
            <p className="text-textSecondary mb-2">@{usuario.nombre_usuario}</p>
            <p className="text-textSecondary text-sm mb-4">{usuario.email}</p>
            <span className="inline-block px-4 py-2 rounded-full bg-primary/10 text-primary font-bold text-sm">
              Rating: {usuario.rating}
            </span>
          </div>

          <div className="mt-6 space-y-3">
            <div className="flex items-center gap-3 text-textSecondary">
              <Mail size={20} />
              <span className="text-sm">{usuario.email}</span>
            </div>
            {usuario.ciudad && usuario.pais && (
              <div className="flex items-center gap-3 text-textSecondary">
                <Calendar size={20} />
                <span className="text-sm">{usuario.ciudad}, {usuario.pais}</span>
              </div>
            )}
          </div>
        </Card>

        {/* Estadísticas */}
        <Card className="lg:col-span-2">
          <h3 className="text-2xl font-bold text-textPrimary mb-6">Estadísticas</h3>
          
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <div className="bg-background rounded-xl p-4 text-center">
              <Trophy size={32} className="text-primary mx-auto mb-2" />
              <p className="text-3xl font-black text-textPrimary">{usuario.partidos_jugados}</p>
              <p className="text-textSecondary text-sm">Partidos Jugados</p>
            </div>
            <div className="bg-background rounded-xl p-4 text-center">
              <Target size={32} className="text-secondary mx-auto mb-2" />
              <p className="text-3xl font-black text-textPrimary">{usuario.rating}</p>
              <p className="text-textSecondary text-sm">Rating Actual</p>
            </div>
            <div className="bg-background rounded-xl p-4 text-center">
              <TrendingUp size={32} className="text-accent mx-auto mb-2" />
              <p className="text-3xl font-black text-textPrimary">
                {usuario.sexo === 'M' ? '♂' : '♀'}
              </p>
              <p className="text-textSecondary text-sm">Género</p>
            </div>
          </div>

          <div className="mt-6 bg-background rounded-xl p-6">
            <h4 className="text-lg font-bold text-textPrimary mb-4">Información</h4>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-textSecondary">Usuario:</span>
                <span className="text-textPrimary font-bold">{usuario.nombre_usuario}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-textSecondary">Email:</span>
                <span className="text-textPrimary font-bold">{usuario.email}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-textSecondary">Rating:</span>
                <span className="text-primary font-bold text-xl">{usuario.rating}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-textSecondary">Partidos:</span>
                <span className="text-textPrimary font-bold">{usuario.partidos_jugados}</span>
              </div>
              {usuario.id_categoria && (
                <div className="flex justify-between">
                  <span className="text-textSecondary">Categoría ID:</span>
                  <span className="text-textPrimary font-bold">{usuario.id_categoria}</span>
                </div>
              )}
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
