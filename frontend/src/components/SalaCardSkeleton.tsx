import { motion } from 'framer-motion';

export default function SalaCardSkeleton() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="h-full"
    >
      <div className="relative bg-cardBg/95 backdrop-blur-sm rounded-lg md:rounded-xl overflow-hidden border border-cardBorder h-full flex flex-col">
        <div className="p-3 md:p-5 relative flex flex-col h-full animate-pulse">
          <div className="space-y-2 md:space-y-3 flex-1 flex flex-col">
            {/* Header skeleton */}
            <div className="flex items-center justify-between gap-2 md:gap-3">
              <div className="flex-1 min-w-0">
                <div className="h-4 md:h-6 bg-cardBorder rounded w-3/4 mb-1 md:mb-2"></div>
                <div className="h-3 md:h-4 bg-cardBorder rounded w-1/2"></div>
              </div>
              <div className="h-6 md:h-8 w-16 md:w-20 bg-cardBorder rounded-full flex-shrink-0"></div>
            </div>

            {/* Content skeleton */}
            <div className="relative bg-background/50 rounded-md md:rounded-lg p-2 md:p-4 backdrop-blur-sm flex-1">
              <div className="grid grid-cols-3 gap-2 md:gap-4">
                {/* Equipo A */}
                <div className="text-center">
                  <div className="bg-primary/10 rounded p-1.5 md:p-2 mb-1 md:mb-2">
                    <div className="h-2 md:h-3 bg-cardBorder rounded w-full mb-1"></div>
                    <div className="h-2 md:h-3 bg-cardBorder rounded w-full mb-0.5"></div>
                    <div className="h-2 md:h-3 bg-cardBorder rounded w-full"></div>
                  </div>
                  <div className="h-8 md:h-12 bg-cardBorder rounded w-full"></div>
                </div>

                {/* VS */}
                <div className="flex items-center justify-center">
                  <div className="bg-cardBorder rounded-full w-8 h-8 md:w-12 md:h-12"></div>
                </div>

                {/* Equipo B */}
                <div className="text-center">
                  <div className="bg-secondary/10 rounded p-1.5 md:p-2 mb-1 md:mb-2">
                    <div className="h-2 md:h-3 bg-cardBorder rounded w-full mb-1"></div>
                    <div className="h-2 md:h-3 bg-cardBorder rounded w-full mb-0.5"></div>
                    <div className="h-2 md:h-3 bg-cardBorder rounded w-full"></div>
                  </div>
                  <div className="h-8 md:h-12 bg-cardBorder rounded w-full"></div>
                </div>
              </div>
            </div>

            {/* Footer skeleton */}
            <div className="flex gap-1.5 md:gap-2 pt-2 md:pt-3 mt-auto">
              <div className="flex-1 h-8 md:h-10 bg-cardBorder rounded"></div>
              <div className="w-8 md:w-10 h-8 md:h-10 bg-cardBorder rounded"></div>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
