import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { User, MapPin, Trophy, Edit3, Save, X, AlertCircle, Globe } from 'lucide-react';
import Card from '../components/Card';
import Button from '../components/Button';
import Input from '../components/Input';
import RatingProgressBar from '../components/RatingProgressBar';
import { useAuth } from '../context/AuthContext';
import { authService } from '../services/auth.service';

interface Categoria {
  id_categoria: number;
  nombre: string;
  descripcion: string;
  rating_min: number;
  rating_max: number;
}

export default function MiPerfil() {
  const { usuario } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [perfilCompleto, setPerfilCompleto] = useState(true);
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  
  const [formData, setFormData] = useState({
    nombre: '',
    apellido: '',
    sexo: 'masculino' as 'masculino' | 'femenino',
    id_categoria_inicial: 0,
    ciudad: '',
    pais: 'Argentina'
  });

  // Cargar categorías y verificar perfil
  useEffect(() => {
    const cargarDatos = async () => {
      try {
        // Cargar categorías
        const response = await fetch(`${import.meta.env.VITE_API_URL}/auth/categorias`);
        if (response.ok) {
          const data = await response.json();
          setCategorias(data);
        }

        // Verificar si el perfil está completo
        const completo = await authService.checkProfileComplete();
        setPerfilCompleto(completo);
        if (!completo) {
          setIsEditing(true);
        }
      } catch (error) {
        console.log('Error cargando datos:', error);
        setPerfilCompleto(false);
        setIsEditing(true);
      }
    };

    if (usuario) {
      cargarDatos();
      // Cargar datos del usuario si existen
      setFormData({
        nombre: usuario.nombre || '',
        apellido: '',
        sexo: 'masculino',
        id_categoria_inicial: 0,
        ciudad: '',
        pais: 'Argentina'
      });
    }
  }, [usuario]);

  const handleSave = async () => {
    if (!formData.nombre || !formData.apellido || !formData.id_categoria_inicial) {
      setError('Por favor completa todos los campos obligatorios');
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      await authService.completarPerfil(formData);

      setSuccess('Perfil actualizado correctamente');
      setPerfilCompleto(true);
      setIsEditing(false);
      
      setTimeout(() => setSuccess(''), 3000);
    } catch (err: any) {
      setError(err.message || 'Error al actualizar el perfil');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    setIsEditing(false);
    setError('');
    if (usuario) {
      setFormData({
        nombre: usuario.nombre || '',
        apellido: '',
        sexo: 'masculino',
        id_categoria_inicial: 0,
        ciudad: '',
        pais: 'Argentina'
      });
    }
  };

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

      {/* Alerta si el perfil no está completo */}
      {!perfilCompleto && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-amber-500/10 border border-amber-500/30 rounded-xl p-4"
        >
          <div className="flex items-center gap-3">
            <AlertCircle size={24} className="text-amber-500" />
            <div>
              <p className="text-amber-500 font-bold">Perfil Incompleto</p>
              <p className="text-textSecondary text-sm">
                Completa tu información para acceder a todas las funcionalidades
              </p>
            </div>
          </div>
        </motion.div>
      )}

      {/* Mensajes de éxito/error */}
      {success && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-secondary/10 border border-secondary/30 rounded-xl p-4"
        >
          <p className="text-secondary font-bold">{success}</p>
        </motion.div>
      )}

      {error && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-red-500/10 border border-red-500/30 rounded-xl p-4"
        >
          <p className="text-red-500 font-bold">{error}</p>
        </motion.div>
      )}

      {/* Información Personal */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <Card>
          <div className="p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-textPrimary flex items-center gap-2">
                <User size={24} className="text-primary" />
                Información Personal
              </h2>
              {!isEditing ? (
                <Button variant="ghost" onClick={() => setIsEditing(true)}>
                  <Edit3 size={18} />
                  Editar
                </Button>
              ) : (
                <div className="flex gap-2">
                  <Button variant="ghost" onClick={handleCancel} disabled={loading}>
                    <X size={18} />
                    Cancelar
                  </Button>
                  <Button variant="primary" onClick={handleSave} disabled={loading}>
                    <Save size={18} />
                    {loading ? 'Guardando...' : 'Guardar'}
                  </Button>
                </div>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Nombre */}
              <div>
                <label className="block text-textSecondary text-sm font-medium mb-2">
                  Nombre *
                </label>
                {isEditing ? (
                  <Input
                    value={formData.nombre}
                    onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
                    placeholder="Tu nombre"
                    required
                  />
                ) : (
                  <p className="text-textPrimary font-semibold">{formData.nombre || 'No especificado'}</p>
                )}
              </div>

              {/* Apellido */}
              <div>
                <label className="block text-textSecondary text-sm font-medium mb-2">
                  Apellido *
                </label>
                {isEditing ? (
                  <Input
                    value={formData.apellido}
                    onChange={(e) => setFormData({ ...formData, apellido: e.target.value })}
                    placeholder="Tu apellido"
                    required
                  />
                ) : (
                  <p className="text-textPrimary font-semibold">{formData.apellido || 'No especificado'}</p>
                )}
              </div>

              {/* Email (no editable) */}
              <div>
                <label className="block text-textSecondary text-sm font-medium mb-2">Email</label>
                <p className="text-textPrimary font-semibold">{usuario.email}</p>
                <p className="text-textSecondary text-xs mt-1">No se puede modificar</p>
              </div>

              {/* Sexo */}
              <div>
                <label className="block text-textSecondary text-sm font-medium mb-2">
                  Sexo *
                </label>
                {isEditing ? (
                  <div className="grid grid-cols-2 gap-3">
                    {[
                      { value: 'masculino', label: 'Masculino', icon: '♂' },
                      { value: 'femenino', label: 'Femenino', icon: '♀' }
                    ].map((gen) => (
                      <motion.button
                        key={gen.value}
                        type="button"
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => setFormData({ ...formData, sexo: gen.value as any })}
                        className={`py-2 px-4 rounded-lg font-bold transition-all flex items-center justify-center gap-2 ${
                          formData.sexo === gen.value
                            ? 'bg-gradient-to-r from-primary to-blue-600 text-white'
                            : 'bg-cardBorder text-textSecondary hover:text-textPrimary'
                        }`}
                      >
                        <span className="text-xl">{gen.icon}</span>
                        <span>{gen.label}</span>
                      </motion.button>
                    ))}
                  </div>
                ) : (
                  <p className="text-textPrimary font-semibold">
                    {formData.sexo === 'masculino' ? '♂ Masculino' : '♀ Femenino'}
                  </p>
                )}
              </div>

              {/* Ciudad */}
              <div>
                <label className="block text-textSecondary text-sm font-medium mb-2">
                  <div className="flex items-center gap-2">
                    <MapPin size={16} />
                    Ciudad
                  </div>
                </label>
                {isEditing ? (
                  <Input
                    value={formData.ciudad}
                    onChange={(e) => setFormData({ ...formData, ciudad: e.target.value })}
                    placeholder="Buenos Aires"
                  />
                ) : (
                  <p className="text-textPrimary font-semibold">{formData.ciudad || 'No especificado'}</p>
                )}
              </div>

              {/* País */}
              <div>
                <label className="block text-textSecondary text-sm font-medium mb-2">
                  <div className="flex items-center gap-2">
                    <Globe size={16} />
                    País
                  </div>
                </label>
                {isEditing ? (
                  <Input
                    value={formData.pais}
                    onChange={(e) => setFormData({ ...formData, pais: e.target.value })}
                    placeholder="Argentina"
                  />
                ) : (
                  <p className="text-textPrimary font-semibold">{formData.pais || 'No especificado'}</p>
                )}
              </div>
            </div>

            {isEditing && (
              <div className="mt-6 p-4 bg-primary/10 border border-primary/30 rounded-xl">
                <p className="text-primary text-sm">
                  <strong>Nota:</strong> Los campos marcados con * son obligatorios.
                </p>
              </div>
            )}
          </div>
        </Card>
      </motion.div>

      {/* Categoría */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <Card>
          <div className="p-6">
            <h2 className="text-2xl font-bold text-textPrimary flex items-center gap-2 mb-6">
              <Trophy size={24} className="text-accent" />
              Categoría
            </h2>

            <div>
              <label className="block text-textSecondary text-sm font-medium mb-2">
                Categoría Inicial *
              </label>
              {isEditing ? (
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {categorias.map((cat) => (
                    <motion.button
                      key={cat.id_categoria}
                      type="button"
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => setFormData({ ...formData, id_categoria_inicial: cat.id_categoria })}
                      className={`p-4 rounded-lg font-bold transition-all text-left ${
                        formData.id_categoria_inicial === cat.id_categoria
                          ? 'bg-gradient-to-r from-accent to-yellow-500 text-white'
                          : 'bg-cardBorder text-textSecondary hover:text-textPrimary'
                      }`}
                    >
                      <div className="text-2xl font-black mb-1">{cat.nombre}</div>
                      <div className="text-xs opacity-80">
                        {cat.rating_min && cat.rating_max 
                          ? `${cat.rating_min}-${cat.rating_max}` 
                          : cat.rating_min 
                          ? `${cat.rating_min}+` 
                          : 'Inicial'}
                      </div>
                    </motion.button>
                  ))}
                </div>
              ) : (
                <p className="text-textPrimary font-semibold text-2xl">
                  {categorias.find(c => c.id_categoria === formData.id_categoria_inicial)?.nombre || 'No especificado'}
                </p>
              )}
            </div>
          </div>
        </Card>
      </motion.div>

      {/* Rating y Progreso */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <Card>
          <div className="p-6">
            <h2 className="text-2xl font-bold text-textPrimary flex items-center gap-2 mb-6">
              <Trophy size={24} className="text-accent" />
              Mi Rating
            </h2>

            <div className="mb-6">
              <RatingProgressBar
                currentRating={1250}
                size="lg"
                showLabel={true}
              />
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              <div className="text-center">
                <p className="text-4xl font-black text-primary mb-2">1250</p>
                <p className="text-textSecondary text-sm">Rating Actual</p>
              </div>
              <div className="text-center">
                <p className="text-4xl font-black text-secondary mb-2">28</p>
                <p className="text-textSecondary text-sm">Partidos</p>
              </div>
              <div className="text-center">
                <p className="text-4xl font-black text-accent mb-2">75%</p>
                <p className="text-textSecondary text-sm">Win Rate</p>
              </div>
              <div className="text-center">
                <p className="text-4xl font-black text-textPrimary mb-2">#42</p>
                <p className="text-textSecondary text-sm">Ranking</p>
              </div>
            </div>
          </div>
        </Card>
      </motion.div>
    </div>
  );
}
