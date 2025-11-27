import { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Camera, Save, X, MapPin, User, Award } from 'lucide-react';
import { ref, uploadBytes, getDownloadURL } from 'firebase/storage';
import { storage } from '../config/firebase';
import { useAuth } from '../context/AuthContext';
import Button from '../components/Button';
import Input from '../components/Input';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function EditarPerfil() {
  const { usuario, updateProfile } = useAuth();
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [loading, setLoading] = useState(false);
  const [uploadingPhoto, setUploadingPhoto] = useState(false);
  const [error, setError] = useState('');
  const [photoPreview, setPhotoPreview] = useState<string | null>(
    usuario?.foto_perfil || null
  );

  const [formData, setFormData] = useState({
    nombre: usuario?.nombre || '',
    apellido: usuario?.apellido || '',
    ciudad: usuario?.ciudad || '',
    pais: usuario?.pais || 'Argentina',
    posicion_preferida: usuario?.posicion_preferida || 'drive',
    mano_dominante: usuario?.mano_dominante || 'derecha',
  });

  const handlePhotoClick = () => {
    fileInputRef.current?.click();
  };

  const handlePhotoChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    // TEMPORALMENTE DESHABILITADO - Pendiente implementación backend
    setError('La funcionalidad de cambiar foto estará disponible próximamente');
    return;
    
    /* 
    const file = e.target.files?.[0];
    if (!file) return;

    // Validar tamaño (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      setError('La imagen no puede superar los 5MB');
      return;
    }

    // Validar tipo
    if (!file.type.startsWith('image/')) {
      setError('Solo se permiten imágenes');
      return;
    }

    try {
      setUploadingPhoto(true);
      setError('');

      // Crear preview local
      const reader = new FileReader();
      reader.onloadend = () => {
        setPhotoPreview(reader.result as string);
      };
      reader.readAsDataURL(file);

      // Subir a Firebase Storage
      const storageRef = ref(storage, `profile-photos/${usuario?.id_usuario}_${Date.now()}`);
      await uploadBytes(storageRef, file);
      const photoURL = await getDownloadURL(storageRef);

      // Actualizar en el backend
      const token = localStorage.getItem('token');
      await axios.put(
        `${API_URL}/usuarios/perfil`,
        { foto_perfil: photoURL },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      // Actualizar contexto local
      updateProfile({ foto_perfil: photoURL });

    } catch (error: any) {
      console.error('Error al subir foto:', error);
      setError('Error al subir la foto. Intenta nuevamente');
      setPhotoPreview(usuario?.foto_perfil || null);
    } finally {
      setUploadingPhoto(false);
    }
    */
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const token = localStorage.getItem('token');
      await axios.put(
        `${API_URL}/usuarios/perfil`,
        formData,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      // Actualizar contexto
      updateProfile(formData);

      navigate('/perfil');
    } catch (error: any) {
      console.error('Error al actualizar perfil:', error);
      setError(error.response?.data?.detail || 'Error al actualizar perfil');
    } finally {
      setLoading(false);
    }
  };

  const esUsuarioGoogle = usuario?.email?.includes('gmail.com') || usuario?.foto_perfil?.includes('googleusercontent.com');

  return (
    <div className="min-h-screen p-4 md:p-6">
      <div className="max-w-2xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-cardBg rounded-xl p-6 md:p-8 border border-cardBorder"
        >
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-2xl md:text-3xl font-black text-textPrimary">
                Editar Perfil
              </h1>
              <p className="text-textSecondary text-sm mt-1">
                Personaliza tu información
              </p>
            </div>
            <button
              onClick={() => navigate('/perfil')}
              className="text-textSecondary hover:text-textPrimary transition-colors"
            >
              <X size={24} />
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Foto de perfil */}
            <div className="flex flex-col items-center">
              <div className="relative group">
                <div className="w-32 h-32 rounded-full overflow-hidden bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
                  {photoPreview ? (
                    <img
                      src={photoPreview}
                      alt="Perfil"
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <span className="text-white text-4xl font-black">
                      {usuario?.nombre?.charAt(0)}{usuario?.apellido?.charAt(0)}
                    </span>
                  )}
                </div>

                {/* Botón de cámara - TEMPORALMENTE DESHABILITADO */}
                {!esUsuarioGoogle && (
                  <button
                    type="button"
                    onClick={handlePhotoClick}
                    disabled={true}
                    className="absolute bottom-0 right-0 bg-gray-500 text-white p-3 rounded-full shadow-lg opacity-50 cursor-not-allowed"
                    title="Próximamente disponible"
                  >
                    <Camera size={20} />
                  </button>
                )}

                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handlePhotoChange}
                  className="hidden"
                />
              </div>

              {esUsuarioGoogle && (
                <p className="text-xs text-textSecondary mt-3 text-center">
                  Tu foto viene de Google
                </p>
              )}

              {!esUsuarioGoogle && (
                <p className="text-xs text-textSecondary mt-3 text-center">
                  Cambio de foto próximamente disponible
                </p>
              )}
            </div>

            {/* Nombre y Apellido */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-textSecondary text-sm font-medium mb-2">
                  Nombre
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 text-textSecondary" size={18} />
                  <Input
                    type="text"
                    value={formData.nombre}
                    onChange={(e) => setFormData({ ...formData, nombre: e.target.value })}
                    placeholder="Tu nombre"
                    required
                    className="pl-10"
                  />
                </div>
              </div>

              <div>
                <label className="block text-textSecondary text-sm font-medium mb-2">
                  Apellido
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 text-textSecondary" size={18} />
                  <Input
                    type="text"
                    value={formData.apellido}
                    onChange={(e) => setFormData({ ...formData, apellido: e.target.value })}
                    placeholder="Tu apellido"
                    required
                    className="pl-10"
                  />
                </div>
              </div>
            </div>

            {/* Ciudad y País */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-textSecondary text-sm font-medium mb-2">
                  Ciudad
                </label>
                <div className="relative">
                  <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 text-textSecondary" size={18} />
                  <Input
                    type="text"
                    value={formData.ciudad}
                    onChange={(e) => setFormData({ ...formData, ciudad: e.target.value })}
                    placeholder="Tu ciudad"
                    className="pl-10"
                  />
                </div>
              </div>

              <div>
                <label className="block text-textSecondary text-sm font-medium mb-2">
                  País
                </label>
                <div className="relative">
                  <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 text-textSecondary" size={18} />
                  <Input
                    type="text"
                    value={formData.pais}
                    onChange={(e) => setFormData({ ...formData, pais: e.target.value })}
                    placeholder="Tu país"
                    className="pl-10"
                  />
                </div>
              </div>
            </div>

            {/* Posición Preferida */}
            <div>
              <label className="block text-textSecondary text-sm font-medium mb-2">
                Posición Preferida
              </label>
              <div className="grid grid-cols-2 gap-3">
                <button
                  type="button"
                  onClick={() => setFormData({ ...formData, posicion_preferida: 'drive' })}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    formData.posicion_preferida === 'drive'
                      ? 'border-primary bg-primary/10 text-primary'
                      : 'border-cardBorder bg-background text-textSecondary hover:border-primary/50'
                  }`}
                >
                  <Award size={24} className="mx-auto mb-2" />
                  <p className="font-bold">Drive</p>
                  <p className="text-xs mt-1">Lado derecho</p>
                </button>

                <button
                  type="button"
                  onClick={() => setFormData({ ...formData, posicion_preferida: 'reves' })}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    formData.posicion_preferida === 'reves'
                      ? 'border-secondary bg-secondary/10 text-secondary'
                      : 'border-cardBorder bg-background text-textSecondary hover:border-secondary/50'
                  }`}
                >
                  <Award size={24} className="mx-auto mb-2" />
                  <p className="font-bold">Revés</p>
                  <p className="text-xs mt-1">Lado izquierdo</p>
                </button>
              </div>
            </div>

            {/* Mano Dominante */}
            <div>
              <label className="block text-textSecondary text-sm font-medium mb-2">
                Mano Dominante
              </label>
              <div className="grid grid-cols-2 gap-3">
                <button
                  type="button"
                  onClick={() => setFormData({ ...formData, mano_dominante: 'derecha' })}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    formData.mano_dominante === 'derecha'
                      ? 'border-accent bg-accent/10 text-accent'
                      : 'border-cardBorder bg-background text-textSecondary hover:border-accent/50'
                  }`}
                >
                  <span className="text-3xl mb-2 block">👉</span>
                  <p className="font-bold">Derecha</p>
                </button>

                <button
                  type="button"
                  onClick={() => setFormData({ ...formData, mano_dominante: 'zurda' })}
                  className={`p-4 rounded-lg border-2 transition-all ${
                    formData.mano_dominante === 'zurda'
                      ? 'border-accent bg-accent/10 text-accent'
                      : 'border-cardBorder bg-background text-textSecondary hover:border-accent/50'
                  }`}
                >
                  <span className="text-3xl mb-2 block">👈</span>
                  <p className="font-bold">Zurda</p>
                </button>
              </div>
            </div>

            {/* Error */}
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-red-500/10 border border-red-500/30 rounded-lg p-3"
              >
                <p className="text-red-500 text-sm">{error}</p>
              </motion.div>
            )}

            {/* Botones */}
            <div className="flex gap-3 pt-4">
              <Button
                type="button"
                variant="ghost"
                onClick={() => navigate('/perfil')}
                className="flex-1"
              >
                Cancelar
              </Button>
              <Button
                type="submit"
                variant="primary"
                disabled={loading}
                className="flex-1 flex items-center justify-center gap-2"
              >
                <Save size={18} />
                {loading ? 'Guardando...' : 'Guardar Cambios'}
              </Button>
            </div>
          </form>
        </motion.div>
      </div>
    </div>
  );
}
