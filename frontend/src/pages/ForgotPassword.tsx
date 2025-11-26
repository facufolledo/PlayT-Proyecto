import { useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate, Link } from 'react-router-dom';
import { Mail, ArrowLeft, CheckCircle } from 'lucide-react';
import Button from '../components/Button';
import Input from '../components/Input';
import CursorTrail from '../components/CursorTrail';
import { authService } from '../services/auth.service';

export default function ForgotPassword() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [emailSent, setEmailSent] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!email) {
      setError('Por favor ingresa tu email');
      return;
    }

    if (!/\S+@\S+\.\S+/.test(email)) {
      setError('Email inválido');
      return;
    }

    setLoading(true);

    try {
      await authService.sendPasswordResetEmail(email);
      setEmailSent(true);
    } catch (err: any) {
      setError(err.message || 'Error al enviar el email de recuperación');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4 relative overflow-hidden">
      <CursorTrail />
      {/* Fondo de pádel */}
      <div className="fixed inset-0 pointer-events-none">
        <div 
          className="absolute inset-0 bg-cover bg-center opacity-30"
          style={{
            backgroundImage: 'url(https://i.ibb.co/wN0RJcvS/padel2.webp)',
          }}
        />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md relative z-10 px-4"
      >
        {/* Logo y título */}
        <div className="text-center mb-6 md:mb-8">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: "spring", stiffness: 200 }}
            className="inline-flex flex-col items-center justify-center mb-3 md:mb-4"
          >
            <img 
              src={`${import.meta.env.BASE_URL}logo-playr.png`}
              alt="PlayR Logo" 
              className="w-20 h-20 md:w-28 md:h-28 mb-2 md:mb-3"
            />
            <h1 className="text-2xl md:text-3xl font-black text-textPrimary">
              Play<span className="text-primary">R</span>
            </h1>
          </motion.div>
          <p className="text-textSecondary text-center text-sm md:text-base">Recupera tu contraseña</p>
        </div>

        {/* Formulario */}
        <div className="bg-cardBg rounded-xl md:rounded-2xl p-5 md:p-8 border border-cardBorder shadow-2xl">
          {emailSent ? (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="text-center py-4 md:py-8"
            >
              <div className="w-16 h-16 md:w-20 md:h-20 bg-primary/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <CheckCircle className="text-primary" size={32} />
              </div>
              <h3 className="text-lg md:text-xl font-bold text-textPrimary mb-2">
                ¡Email enviado!
              </h3>
              <p className="text-textSecondary mb-2 text-sm md:text-base">
                Te enviamos un correo a <span className="text-primary font-bold">{email}</span>
              </p>
              <p className="text-textSecondary text-xs md:text-sm mb-6">
                Haz clic en el enlace del correo para restablecer tu contraseña.
              </p>
              <div className="space-y-3">
                <Button
                  variant="primary"
                  onClick={() => navigate('/login')}
                  className="w-full text-sm md:text-base"
                >
                  Ir a Iniciar Sesión
                </Button>
                <button
                  onClick={() => {
                    setEmailSent(false);
                    setEmail('');
                  }}
                  className="text-textSecondary hover:text-textPrimary text-sm transition-colors w-full"
                >
                  Enviar a otro email
                </button>
              </div>
            </motion.div>
          ) : (
            <>
              <h2 className="text-xl md:text-2xl font-bold text-textPrimary mb-2">
                ¿Olvidaste tu contraseña?
              </h2>
              <p className="text-textSecondary text-xs md:text-sm mb-4 md:mb-6">
                Ingresa tu email y te enviaremos un enlace para restablecer tu contraseña.
              </p>

              {error && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-red-500/10 border border-red-500/50 rounded-lg p-3 mb-4"
                >
                  <p className="text-red-500 text-sm">{error}</p>
                </motion.div>
              )}

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-textSecondary text-xs md:text-sm font-medium mb-1.5 md:mb-2">
                    Email
                  </label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 -translate-y-1/2 text-textSecondary" size={18} />
                    <Input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="tu@email.com"
                      className="pl-10 text-sm md:text-base"
                      autoFocus
                    />
                  </div>
                </div>

                <Button
                  type="submit"
                  variant="primary"
                  className="w-full text-sm md:text-base py-2.5 md:py-3"
                  disabled={loading}
                >
                  {loading ? 'Enviando...' : 'Enviar enlace de recuperación'}
                </Button>
              </form>

              <div className="mt-6 text-center space-y-3">
                <Link 
                  to="/login" 
                  className="text-textSecondary hover:text-primary text-sm transition-colors flex items-center justify-center gap-2"
                >
                  <ArrowLeft size={16} />
                  Volver a Iniciar Sesión
                </Link>
                <p className="text-textSecondary text-sm">
                  ¿No tienes cuenta?{' '}
                  <Link to="/register" className="text-primary hover:text-blue-400 font-bold transition-colors">
                    Regístrate aquí
                  </Link>
                </p>
              </div>
            </>
          )}
        </div>
      </motion.div>
    </div>
  );
}
