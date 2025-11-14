import { motion } from "framer-motion";
import { LogIn } from "lucide-react";
import { useNavigate } from "react-router-dom";
import Logo from "./Logo";

export default function Navbar() {
  const navigate = useNavigate();

  return (
    <motion.nav
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6 }}
      className="fixed top-0 left-0 right-0 z-50 backdrop-blur-md bg-[#0E0F11]/80 border-b border-white/10"
    >
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <motion.div
          className="flex items-center gap-3 cursor-pointer"
          whileHover={{ scale: 1.02 }}
          transition={{ type: "spring", stiffness: 400 }}
          onClick={() => navigate("/")}
        >
          <Logo size={40} />
          <span className="text-2xl font-bold text-white">
            Play<span className="text-[#0071FF]">R</span>
          </span>
        </motion.div>

        <motion.button
          onClick={() => navigate("/dashboard")}
          whileHover={{
            scale: 1.05,
            boxShadow: "0px 0px 20px rgba(0, 255, 163, 0.5)",
            y: -1,
            transition: { type: "spring", stiffness: 400, damping: 10 }
          }}
          whileTap={{ scale: 0.98, y: 0 }}
          className="bg-[#00FFA3] hover:bg-[#00DD8C] text-[#0E0F11] font-bold text-sm px-5 py-2 rounded-lg transition-all flex items-center gap-2 tracking-wide uppercase"
        >
          <LogIn size={16} />
          Ingresar
        </motion.button>
      </div>
    </motion.nav>
  );
}
