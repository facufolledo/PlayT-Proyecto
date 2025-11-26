import { motion } from "framer-motion";
import { ArrowLeft } from "lucide-react";
import { useNavigate } from "react-router-dom";
import Logo from "../components/Logo";

export default function DashboardPlaceholder() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-[#0E0F11] text-white flex flex-col items-center justify-center px-6">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.6 }}
        className="text-center"
      >
        <div className="flex justify-center mb-6">
          <Logo size={100} />
        </div>

        <h1 className="text-4xl md:text-5xl font-bold mb-4">
          Dashboard <span className="text-[#0071FF]">PlayR</span>
        </h1>

        <p className="text-[#9DA3AF] text-lg mb-8">
          El dashboard estará disponible próximamente
        </p>

        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => navigate("/")}
          className="bg-[#181B20] hover:bg-[#1F2329] text-white font-semibold px-6 py-3 rounded-xl flex items-center gap-2 mx-auto transition-all border border-white/10"
        >
          <ArrowLeft size={20} />
          Volver al inicio
        </motion.button>
      </motion.div>
    </div>
  );
}
