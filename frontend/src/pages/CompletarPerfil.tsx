import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { User, MapPin, Trophy, Globe } from 'lucide-react';
import Button from '../components/Button';
import Input from '../components/Input';
import Card from '../components/Card';
import { authService, PerfilCompleto } from '../services/auth.service';
import { useAuth } from '../context/AuthContext';

interface Categoria {
  id_categoria: number;
  nombre: string;
  descripcion: string;
  rating_min: number;
  rating_max: number;
}

export default function CompletarPerfil() {
  const navigate = useNavigate();
  const { usuario } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  
  const [formData, setFormData] = useState<PerfilCompleto>({
    nombre: '',
    apellido: '',
    sexo: 'masculino',
    id_categoria_inicial: 0,
    ciudad: '',
    pais: 'Argentina'
  });

  // Cargar categorías desde el backend
  useEffect(() => {
    const cargarCategorias = async () => {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/auth/categorias`);
        if (response.ok) {
          const data = await response.json();
          setCategorias(data);
          if (data.length > 0) {
            setFormData(prev => ({ ...prev, id_categoria_inicial: data[0].id_categoria }));
          }
        }
      } catch (error) {
        console.error('Error cargando categorías:', error);
      }
    };
    cargarCategorias();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await authService.completarPerfil(formData);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Error al completar el perfil');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-3xl"
      >
        <Card>
          <div className="mb-6">
            <h1 className="text-3xl font-black text-textPrimary mb-2">
              Completá tu Perfil
            </h1>
            <p className="text-textSecondary">
              Necesitamos algunos datos adicionales para crear tu cuenta de jugador
            </p>
            {usuario && (
              <p className="text-primary text-sm mt-2">
                Registrado como: {usuario.email}
              </p>
            )}
          </div>

          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-red-500/10 border border-red-500/50 rounded-lg p-3 mb-4"
            >
              <p className="text-red-500 text-sm">{error}</p>
            </motion.div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Datos Personales */}
            <div>
              <h3 className="text-lg font-bold text-textPrimary mb-4 flex items-center gap-2">
                <User size={20} className="text-primary" />
                Datos Personales
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-textSecondary text-sm font-medium mb-2">
                    Nombre *
                  </label>
                  <Input
                    value={formData.nombre}
                    onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
                    placeholder="Juan"
                    required
                  />
                </div>
                <div>
                  <label className="block text-textSecondary text-sm font-medium mb-2">
                    Apellido *
                  </label>
                  <Input
                    value={formData.apellido}
                    onChange={(e) => setFormData({ ...formData, apellido: e.target.value })}
                    placeholder="Pérez"
                    required
                  />
                </div>
              </div>
            </div>

            {/* Sexo */}
            <div>
              <label className="block text-textSecondary text-sm font-medium mb-2">
                Sexo *
              </label>
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
                    className={`py-3 px-4 rounded-lg font-bold transition-all flex items-center justify-center gap-2 ${
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
            </div>

            {/* Categoría Inicial */}
            <div>
              <h3 className="text-lg font-bold text-textPrimary mb-4 flex items-center gap-2">
                <Trophy size={20} className="text-accent" />
                Categoría Inicial
              </h3>
              
              <div className="mb-4">
                <label className="block text-textSecondary text-sm font-medium mb-2">
                  Selecciona tu categoría *
                </label>
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
              </div>
            </div>

            {/* Ubicación (Opcional) */}
            <div>
              <h3 className="text-lg font-bold text-textPrimary mb-4">
                Ubicación (Opcional)
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-textSecondary text-sm font-medium mb-2">
                    <div className="flex items-center gap-2">
                      <MapPin size={16} />
                      Ciudad
                    </div>
                  </label>
                  <Input
                    value={formData.ciudad}
                    onChange={(e) => setFormData({ ...formData, ciudad: e.target.value })}
                    placeholder="Buenos Aires"
                  />
                </div>
                <div>
                  <label className="block text-textSecondary text-sm font-medium mb-2">
                    <div className="flex items-center gap-2">
                      <Globe size={16} />
                      País
                    </div>
                  </label>
                  <Input
                    value={formData.pais}
                    onChange={(e) => setFormData({ ...formData, pais: e.target.value })}
                    placeholder="Argentina"
                  />
                </div>
              </div>
            </div>

            {/* Botones */}
            <div className="flex gap-3 pt-4">
              <Button
                type="button"
                variant="ghost"
                onClick={() => navigate('/')}
                className="flex-1"
                disabled={loading}
              >
                Cancelar
              </Button>
              <Button
                type="submit"
                variant="accent"
                className="flex-1"
                disabled={loading}
              >
                {loading ? 'Guardando...' : 'Completar Registro'}
              </Button>
            </div>
          </form>
        </Card>
      </motion.div>
    </div>
  );
}
