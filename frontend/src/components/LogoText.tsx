interface LogoTextProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export default function LogoText({ size = 'md', className = '' }: LogoTextProps) {
  const sizes = {
    sm: 'text-xl',
    md: 'text-2xl md:text-3xl',
    lg: 'text-3xl md:text-4xl'
  };

  return (
    <div className={`inline-flex items-center justify-center ${className}`}>
      <h1 className={`${sizes[size]} font-black text-textPrimary`}>
        Play<span className="text-primary">R</span>
      </h1>
    </div>
  );
}
