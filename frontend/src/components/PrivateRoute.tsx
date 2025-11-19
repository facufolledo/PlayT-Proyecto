import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { motion } from 'framer-motion';

interface PrivateRouteProps {
  children: React.ReactNode;
}

export default function PrivateRoute({ children }: PrivateRouteProps) {
  const { isAuthenticated, isLoading, needsProfileCompletion, firebaseUser, usuario } = useAuth();
  const location = useLocation();

  console.log('🔒 PrivateRoute:', { 
    path: location.pathname,
    isAuthenticated, 
    isLoading, 
    needsProfileCompletion, 
    hasFirebaseUser: !!firebaseUser, 
    hasUsuario: !!usuario 
  });

  if (isLoading) {
    console.log('⏳ PrivateRoute: Loading...');
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full"
        />
      </div>
    );
  }

  if (!isAuthenticated) {
    console.log('❌ PrivateRoute: Not authenticated, redirecting to login');
    return <Navigate to="/login" replace />;
  }

  // Si tiene firebaseUser pero no usuario del backend, necesita completar perfil
  // PERO solo redirigir si NO está ya en la página de completar perfil
  if (firebaseUser && !usuario && needsProfileCompletion && location.pathname !== '/completar-perfil') {
    console.log('📝 PrivateRoute: Needs profile completion, redirecting to completar-perfil');
    return <Navigate to="/completar-perfil" replace />;
  }

  console.log('✅ PrivateRoute: Rendering children');
  return <>{children}</>;
}
