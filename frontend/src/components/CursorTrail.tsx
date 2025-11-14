import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface Trail {
  id: number;
  x: number;
  y: number;
}

export default function CursorTrail() {
  const [trails, setTrails] = useState<Trail[]>([]);

  useEffect(() => {
    let trailId = 0;

    const handleMouseMove = (e: MouseEvent) => {
      const newTrail: Trail = {
        id: trailId++,
        x: e.clientX,
        y: e.clientY,
      };

      setTrails(prev => [...prev, newTrail].slice(-8)); // Mantener solo las últimas 8

      // Limpiar después de un tiempo
      setTimeout(() => {
        setTrails(prev => prev.filter(t => t.id !== newTrail.id));
      }, 400);
    };

    window.addEventListener('mousemove', handleMouseMove);

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
    };
  }, []);

  return (
    <div className="fixed inset-0 pointer-events-none z-50">
      {/* Estela minimalista */}
      <AnimatePresence>
        {trails.map((trail, index) => (
          <motion.div
            key={trail.id}
            initial={{ scale: 1, opacity: 0.5 }}
            animate={{ scale: 0, opacity: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.4, ease: "easeOut" }}
            style={{
              position: 'absolute',
              left: trail.x,
              top: trail.y,
              width: 8 - index * 0.8,
              height: 8 - index * 0.8,
              borderRadius: '50%',
              background: `rgba(0, 85, 255, ${0.5 - index * 0.06})`,
              transform: 'translate(-50%, -50%)',
            }}
          />
        ))}
      </AnimatePresence>
    </div>
  );
}
