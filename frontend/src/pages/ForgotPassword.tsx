import { useState } from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { Mail, ArrowLeft, CheckCircle } from 'lucide-react';
import { sendPasswordResetEmail } from 'firebase/auth';
import { auth } from '../config/firebase';
import Button from '../components/Button';
import Input from '../components/Input';
import Logo from '../components/Logo';

export default function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await sendPasswordResetEmail(auth, email, {
        url: window.location.origin + '/login',
        handleCodeInApp: false,
      });
      setSuccess(true);
    } catch (error: any) {
      console.error('Error al enviar email:', error);
      
      switch (error.code) {
        case 'auth/user-not-found':
          setError('No existe una cuenta con este email');
          break;
        case 'auth/invalid-email':
          setError('Email inválido');
          break;
        case 'auth/too-many-requests':
          setError('Demasiados intentos. Intenta más tarde');
          break;
        default:
          setError('Error al enviar el email. Intenta nuevamente');
      }
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-background via-background to-primary/5">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="w-full max-w-md"
        >
          <div className="bg-cardBg/95 backdrop-blur-xl rounded-2xl p-8 border border-cardBorder shadow-2xl">
            <div className="text-center mb-6">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.2, type: 'spring' }}
                className="inline-flex items-center justify-center w-16 h-16 bg-green-500/20 rounded-full mb-4"
              >
                <CheckCircle size={32} className="text-green-500" />
              </motion.div>
              <h2 className="text-2xl font-black text-textPrimary mb-2">
                ¡Email Enviado!
              </h2>
              <p className="text-textSecondary text-sm">
                Revisa tu bandeja de entrada
              </p>
            </div>

            <div className="bg-primary/10 rounded-lg p-4 mb-6">
              <p className="text-textPrimary text-sm mb-2">
                Te enviamos un email a:
              </p>
              <p className="text-primary font-bold break-all">
                {email}
              </p>
            </div>

            <div className="space-y-3 text-sm text-textSecondary">
              <p>
                📧 Haz clic en el enlace del email para restablecer tu contraseña
              </p>
              <p>
                ⏰ El enlace expira en 1 hora
              </p>
              <p>
                📁 Si no lo ves, revisa tu carpeta de spam
              </p>
            </div>

            <Link to="/login" className="block mt-6">
              <Button variant="primary" className="w-full">
                Volver al Login
              </Button>
            </Link>

            <button
              onClick={() => {
                setSuccess(false);
                setEmail('');
              }}
              className="w-full mt-3 text-sm text-textSecondary hover:text-primary transition-colors"
            >
              Enviar a otro email
            </button>
          </div>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-background via-background to-primary/5">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md"
      >
        <div className="bg-cardBg/95 backdrop-blur-xl rounded-2xl p-8 border border-cardBorder shadow-2xl">
          {/* Logo */}
          <div className="flex justify-center mb-6">
            <Logo />
          </div>

          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-3xl font-black text-textPrimary mb-2">
              ¿Olvidaste tu contraseña?
            </h1>
            <p className="text-textSecondary text-sm">
              No te preocupes, te enviaremos instrucciones para restablecerla
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-textSecondary text-sm font-medium mb-2">
                Email
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 text-textSecondary" size={18} />
                <Input
                  type="email"
                  placeholder="tu@email.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  disabled={loading}
                  className="pl-10"
                />
              </div>
            </div>

            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-red-500/10 border border-red-500/30 rounded-lg p-3"
              >
                <p className="text-red-500 text-sm">{error}</p>
              </motion.div>
            )}

            <Button
              type="submit"
              variant="primary"
              disabled={loading || !email}
              className="w-full"
            >
              {loading ? 'Enviando...' : 'Enviar Email de Recuperación'}
            </Button>
          </form>

          {/* Info adicional */}
          <div className="mt-6 p-4 bg-primary/5 rounded-lg">
            <p className="text-xs text-textSecondary">
              💡 <span className="font-semibold">Nota:</span> Si iniciaste sesión con Google, 
              debes restablecer tu contraseña desde tu cuenta de Google.
            </p>
          </div>

          {/* Back to login */}
          <Link
            to="/login"
            className="flex items-center justify-center gap-2 mt-6 text-sm text-textSecondary hover:text-primary transition-colors"
          >
            <ArrowLeft size={16} />
            Volver al Login
          </Link>
        </div>

        {/* Footer */}
        <p className="text-center text-xs text-textSecondary mt-6">
          ¿No tienes cuenta?{' '}
          <Link to="/register" className="text-primary hover:underline font-semibold">
            Regístrate aquí
          </Link>
        </p>
      </motion.div>
    </div>
  );
}
