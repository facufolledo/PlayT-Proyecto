import { ButtonHTMLAttributes, ReactNode } from 'react';
import { motion } from 'framer-motion';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode;
  variant?: 'primary' | 'secondary' | 'accent' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
}

export default function Button({
  children,
  variant = 'primary',
  size = 'md',
  className = '',
  ...props
}: ButtonProps) {
  const baseStyles = 'font-bold rounded-xl transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed relative overflow-hidden group';

  const variants = {
    primary: 'bg-gradient-to-r from-primary to-blue-600 text-white hover:shadow-lg hover:shadow-primary/50 shadow-md shadow-primary/30',
    secondary: 'bg-gradient-to-r from-secondary to-pink-600 text-white hover:shadow-lg hover:shadow-secondary/50 shadow-md shadow-secondary/30',
    accent: 'bg-gradient-to-r from-accent to-yellow-500 text-background hover:shadow-lg hover:shadow-accent/50 shadow-md shadow-accent/30 font-black',
    ghost: 'bg-cardBg text-textPrimary hover:bg-cardBorder border border-cardBorder hover:border-primary/50 shadow-sm hover:shadow-md',
    danger: 'bg-gradient-to-r from-red-500 to-red-600 text-white hover:shadow-lg hover:shadow-red-500/50 shadow-md shadow-red-500/30',
  };

  const sizes = {
    sm: 'px-4 py-2 text-sm',
    md: 'px-6 py-3 text-base',
    lg: 'px-8 py-4 text-lg',
  };

  return (
    <motion.button
      whileHover={{ scale: 1.03, y: -2 }}
      whileTap={{ scale: 0.97 }}
      transition={{ type: "spring", stiffness: 400, damping: 17 }}
      className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${className}`}
      {...props}
    >
      <span className="relative z-10">{children}</span>
    </motion.button>
  );
}
