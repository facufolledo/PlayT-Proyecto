import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

interface UserLinkProps {
  userId: number | string;
  nombre: string;
  apellido?: string;
  nombreUsuario?: string; // Opcional - si no se pasa, usa el ID
  className?: string;
  showRating?: boolean;
  rating?: number;
  size?: 'sm' | 'md' | 'lg';
}

/**
 * Componente para mostrar nombre de usuario clickeable
 * Redirige al perfil: /perfil/:id o /{nombreUsuario}
 */
export default function UserLink({
  userId,
  nombre,
  apellido,
  nombreUsuario,
  className = '',
  showRating = false,
  rating,
  size = 'md'
}: UserLinkProps) {
  const { usuario } = useAuth();
  
  const userIdNum = typeof userId === 'string' ? parseInt(userId) : userId;
  const esUsuarioActual = usuario?.id_usuario === userIdNum;
  
  // Verificar si tenemos un ID válido para navegar
  const tieneIdValido = userIdNum && userIdNum > 0 && !isNaN(userIdNum);
  const puedeNavegar = tieneIdValido || (nombreUsuario && nombreUsuario.trim() !== '');
  
  const sizeClasses = {
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-base'
  };
  
  const displayName = apellido ? `${nombre} ${apellido}` : nombre;
  
  // Determinar la URL de destino
  let destino = '/perfil';
  if (!esUsuarioActual) {
    if (nombreUsuario && nombreUsuario.trim() !== '') {
      // Usar la nueva ruta por username
      destino = `/jugador/${nombreUsuario}`;
    } else if (tieneIdValido) {
      // Fallback a ID si no hay username
      destino = `/perfil/${userIdNum}`;
    }
  }
  
  // Si no puede navegar, mostrar solo texto sin link
  if (!puedeNavegar) {
    return (
      <span className={`${sizeClasses[size]} font-semibold text-textPrimary ${className}`}>
        {displayName}
        {showRating && rating && (
          <span className="ml-1 text-textSecondary font-normal">({rating})</span>
        )}
      </span>
    );
  }
  
  return (
    <Link
      to={destino}
      onClick={(e) => e.stopPropagation()}
      className={`
        ${sizeClasses[size]}
        font-semibold text-textPrimary hover:text-primary 
        transition-colors cursor-pointer hover:underline
        ${className}
      `}
    >
      {displayName}
      {showRating && rating && (
        <span className="ml-1 text-textSecondary font-normal">
          ({rating})
        </span>
      )}
    </Link>
  );
}

/**
 * Versión simplificada que acepta ID, nombre y opcionalmente nombreUsuario
 */
export function PlayerLink({
  id,
  nombre,
  nombreUsuario,
  className = '',
  size = 'md'
}: {
  id: number | string;
  nombre: string;
  nombreUsuario?: string;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}) {
  return (
    <UserLink
      userId={id}
      nombre={nombre}
      nombreUsuario={nombreUsuario}
      className={className}
      size={size}
    />
  );
}


interface UserAvatarLinkProps {
  userId: number;
  nombre: string;
  apellido?: string;
  nombreUsuario: string; // Requerido para la URL
  fotoUrl?: string | null;
  size?: 'sm' | 'md' | 'lg';
  showName?: boolean;
  className?: string;
}

/**
 * Avatar clickeable que lleva al perfil
 */
export function UserAvatarLink({
  userId,
  nombre,
  apellido,
  nombreUsuario,
  fotoUrl,
  size = 'md',
  showName = true,
  className = ''
}: UserAvatarLinkProps) {
  const { usuario } = useAuth();
  
  const esUsuarioActual = usuario?.id_usuario === userId;
  const destino = esUsuarioActual ? '/perfil' : `/jugador/${nombreUsuario}`;
  
  const sizeClasses = {
    sm: 'w-6 h-6 text-xs',
    md: 'w-8 h-8 text-sm',
    lg: 'w-12 h-12 text-lg'
  };
  
  const iniciales = `${nombre?.charAt(0) || ''}${apellido?.charAt(0) || ''}`;
  
  return (
    <Link
      to={destino}
      onClick={(e) => e.stopPropagation()}
      className={`flex items-center gap-2 hover:opacity-80 transition-opacity ${className}`}
    >
      <div className={`
        ${sizeClasses[size]}
        rounded-full bg-gradient-to-br from-primary to-secondary 
        flex items-center justify-center text-white font-bold
        overflow-hidden flex-shrink-0
      `}>
        {fotoUrl ? (
          <img src={fotoUrl} alt={nombre} className="w-full h-full object-cover" />
        ) : (
          <span>{iniciales}</span>
        )}
      </div>
      {showName && (
        <span className="font-semibold text-textPrimary hover:text-primary transition-colors">
          {nombre} {apellido}
        </span>
      )}
    </Link>
  );
}
