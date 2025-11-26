import { motion } from "framer-motion";

interface MotionButtonProps {
  label: string;
  onClick: () => void;
  variant?: "primary" | "accent";
  icon?: React.ReactNode;
}

export default function MotionButton({
  label,
  onClick,
  variant = "primary",
  icon
}: MotionButtonProps) {
  const variantStyles = {
    primary: "bg-[#0071FF] hover:bg-[#005CE6]",
    accent: "bg-[#00FFA3] hover:bg-[#00DD8C] text-[#0E0F11]"
  };

  return (
    <motion.button
      whileHover={{
        scale: 1.05,
        boxShadow: variant === "primary"
          ? "0px 0px 25px rgba(0, 113, 255, 0.6)"
          : "0px 0px 25px rgba(0, 255, 163, 0.6)",
        y: -2,
        transition: { type: "spring", stiffness: 400, damping: 10 }
      }}
      whileTap={{ scale: 0.98, y: 0 }}
      onClick={onClick}
      className={`${variantStyles[variant]} text-white font-semibold text-base px-8 py-3 rounded-xl flex items-center gap-2 transition-all shadow-lg`}
    >
      {label} {icon}
    </motion.button>
  );
}
