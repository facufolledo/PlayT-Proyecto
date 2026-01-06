import { motion } from 'framer-motion';

interface LogoProps {
  size?: number;
  className?: string;
  animated?: boolean;
  clickable?: boolean;
}

export default function Logo({ size = 48, className = '', animated = false, clickable = false }: LogoProps) {
  const handleClick = () => {
    if (clickable) {
      window.location.reload();
    }
  };

  const LogoImage = (
    <img
      src={`${import.meta.env.BASE_URL}logo-Drive+.png`}
      alt="Drive+ Logo"
      width={size}
      height={size}
      className={`${className} object-contain ${clickable ? 'cursor-pointer' : ''}`}
      style={{ width: size, height: size }}
      onClick={handleClick}
    />
  );

  if (animated) {
    return (
      <motion.div
        initial={{ scale: 0, rotate: -180 }}
        animate={{ scale: 1, rotate: 0 }}
        transition={{ type: "spring", stiffness: 200, damping: 15 }}
        whileHover={{ scale: 1.05 }}
        onClick={handleClick}
        className={clickable ? 'cursor-pointer' : ''}
      >
        {LogoImage}
      </motion.div>
    );
  }

  return LogoImage;
}
