import { motion } from 'framer-motion';

interface LogoProps {
  size?: number;
  className?: string;
  animated?: boolean;
}

export default function Logo({ size = 48, className = '', animated = false }: LogoProps) {
  const LogoImage = (
    <img
      src={`${import.meta.env.BASE_URL}logo-playr.png`}
      alt="PlayR Logo"
      width={size}
      height={size}
      className={`${className} object-contain`}
      style={{ width: size, height: size }}
    />
  );

  if (animated) {
    return (
      <motion.div
        initial={{ scale: 0, rotate: -180 }}
        animate={{ scale: 1, rotate: 0 }}
        transition={{ type: "spring", stiffness: 200, damping: 15 }}
        whileHover={{ scale: 1.05 }}
      >
        {LogoImage}
      </motion.div>
    );
  }

  return LogoImage;
}
