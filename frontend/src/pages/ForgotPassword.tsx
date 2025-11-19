import { useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate, Link } from 'react-router-dom';
import { Mail, ArrowLeft } from 'lucide-react';
import Button from '../components/Button';
import Input from '../components/Input';
import CursorTrail from '../components/CursorTrail';
import { authService } from '../services/auth.service';

export default function ForgotPassword() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [emailSent, setEmailSent] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!email) {
      setError('El email es requerido');
      return;
    }

    if (!/\S+@\S+\.\S+/.test(email)) {
      setError('Email inválido');
      return;
    }

    setIsLoading(true);

    try {
      await authService.sendPasswordResetEmail(email);
      setEmailSent(true);
    } catch (err: any) {
      setError(err.message || 'Error al enviar email de recuperación');
    } finally {
      setIsLoading(false);
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
        className="w-full max-w-md relative z-10"
      >
        {/* Logo y título */}
        <div className="text-center mb-8">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: "spring", stiffness: 200 }}
            className="inline-flex flex-col items-center justify-center mb-4"
          >
            <img 
              src="/logo playR.png" 
              alt="PlayR Logo" 
              className="w-32 h-32 mb-4"
            />
            <h1 className="text-4xl font-black text-textPrimary">
              Play<span className="text-primary">R</span>
            </h1>
          </motion.div>
          <p className="text-textSecondary text-center">Recupera tu contraseña</p>
        </div>

        {/* Formulario */}
        <div className="bg-cardBg rounded-2xl p-8 border border-cardBorder shadow-2xl">
          <h2 className="text-2xl font-bold text-textPrimary mb-6">¿Olvidaste tu contraseña?</h2>

          {emailSent ? (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="text-center py-8"
            >
              <div className="w-16 h-16 bg-primary/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <Mail className="text-primary" size={32} />
              </div>
              <h3 className="text-xl font-bold text-textPrimary mb-2">
                ¡Email enviado!
              </h3>
              <p className="text-textSecondary mb-4">
                Te enviamos un correo a <span className="text-primary font-bold">{email}</span>
              </p>
              <p className="text-textSecondary text-sm mb-6">
                Revisa tu bandeja de entrada y haz clic en el enlace para restablecer tu contraseña.
              </p>
              <Button
                variant="primary"
                onClick={() => navigate('/login')}
                className="w-full"
              >
                Volver a Iniciar Sesión
              </Button>
            </motion.div>
          ) : (
            <>
              <p className="text-textSecondary text-sm mb-6">
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
                  <label className="block text-textSecondary text-sm font-medium mb-2">
                    Email
                  </label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 -translate-y-1/2 text-textSecondary" size={20} />
                    <Input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="tu@email.com"
                      className="pl-10"
                    />
                  </div>
                </div>

                <Button
                  type="submit"
                  variant="primary"
                  className="w-full"
                  disabled={isLoading}
                >
                  {isLoading ? 'Enviando...' : 'Enviar Email de Recuperación'}
                </Button>
              </form>

              <div className="mt-6 text-center">
                <Link 
                  to="/login" 
                  className="text-textSecondary hover:text-textPrimary text-sm transition-colors inline-flex items-center gap-2"
                >
                  <ArrowLeft size={16} />
                  Volver a Iniciar Sesión
                </Link>
              </div>
            </>
          )}
        </div>
      </motion.div>
    </div>
  );
}
