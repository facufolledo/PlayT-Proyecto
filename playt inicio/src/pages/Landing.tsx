import { motion } from "framer-motion";
import { ArrowRight, Trophy, Users2, TrendingUp, Swords } from "lucide-react";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import MotionButton from "../components/MotionButton";

export default function Landing() {
  const navigate = useNavigate();

  const features = [
    {
      icon: <Trophy size={36} />,
      title: "Torneos",
      description: "Organizá y gestioná torneos profesionales"
    },
    {
      icon: <Users2 size={36} />,
      title: "Jugadores",
      description: "Seguí el rendimiento de cada jugador"
    },
    {
      icon: <TrendingUp size={36} />,
      title: "Estadísticas",
      description: "Análisis detallado en tiempo real"
    },
    {
      icon: <Swords size={36} />,
      title: "Partidos",
      description: "Control completo de cada encuentro"
    }
  ];

  return (
    <div className="min-h-screen bg-[#0E0F11] text-white relative overflow-hidden">
      {/* Imagen de fondo de pádel */}
      <div
        className="absolute inset-0"
        style={{
          backgroundImage: `linear-gradient(rgba(14, 15, 17, 0.65), rgba(14, 15, 17, 0.75)), url('https://i.ibb.co/LD3mCF7g/padel.webp')`,
          backgroundSize: "cover",
          backgroundPosition: "center",
          backgroundRepeat: "no-repeat"
        }}
      />

      {/* Overlay adicional para mejor contraste */}
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-[#0E0F11]/30 to-[#0E0F11]/90" />

      <Navbar />

      <div className="relative z-10 flex flex-col items-center justify-center min-h-screen px-6 pt-16 pb-20">
        <motion.div
          initial={{ opacity: 0, y: 40, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="text-center max-w-5xl"
        >
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="mb-8"
          >
            <h1 className="text-7xl md:text-8xl font-bold mb-6 leading-tight">
              Bienvenido a{" "}
              <span className="text-[#0071FF]">Play</span>
              <span className="text-[#0071FF]">R</span>
            </h1>
          </motion.div>

          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            className="text-2xl md:text-3xl text-[#9DA3AF] mb-14 leading-relaxed"
          >
            Gestioná partidos, torneos y evaluá tus rendimientos
            <br />
            <span className="text-[#E8E9EB]">Todo en una plataforma profesional</span>
          </motion.p>

          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6, delay: 0.6 }}
            className="mb-20 flex justify-center"
          >
            <MotionButton
              label="Comenzar"
              onClick={() => navigate("/dashboard")}
              variant="primary"
              icon={<ArrowRight size={22} />}
            />
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.8 }}
            className="grid grid-cols-2 md:grid-cols-4 gap-8"
          >
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{
                  duration: 0.5,
                  delay: 0.9 + index * 0.1,
                  type: "spring",
                  stiffness: 100
                }}
                whileHover={{
                  scale: 1.08,
                  y: -8,
                  transition: { type: "spring", stiffness: 400, damping: 10 }
                }}
                className="bg-[#0E0F11]/70 backdrop-blur-sm border border-white/10 hover:border-[#0071FF]/50 rounded-xl p-8 text-center transition-all cursor-pointer group"
              >
                <motion.div
                  className="text-[#0071FF] mb-4 flex justify-center"
                  whileHover={{ rotate: [0, -10, 10, -10, 0], scale: 1.1 }}
                  transition={{ duration: 0.5 }}
                >
                  {feature.icon}
                </motion.div>
                <h3 className="text-[#E8E9EB] font-semibold text-lg mb-2 group-hover:text-white transition-colors">
                  {feature.title}
                </h3>
                <p className="text-[#9DA3AF] text-base group-hover:text-[#B5BBC7] transition-colors">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </motion.div>
        </motion.div>
      </div>

      <Footer />
    </div>
  );
}
