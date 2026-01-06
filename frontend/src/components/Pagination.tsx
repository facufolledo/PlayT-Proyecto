import { motion } from 'framer-motion';
import { ChevronLeft, ChevronRight, MoreHorizontal } from 'lucide-react';
import Button from './Button';

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  showInfo?: boolean;
  totalItems?: number;
  itemsPerPage?: number;
}

export default function Pagination({
  currentPage,
  totalPages,
  onPageChange,
  showInfo = true,
  totalItems = 0,
  itemsPerPage = 20
}: PaginationProps) {
  if (totalPages <= 1) return null;

  const getVisiblePages = () => {
    const delta = 2;
    const range = [];
    const rangeWithDots = [];

    for (let i = Math.max(2, currentPage - delta); i <= Math.min(totalPages - 1, currentPage + delta); i++) {
      range.push(i);
    }

    if (currentPage - delta > 2) {
      rangeWithDots.push(1, '...');
    } else {
      rangeWithDots.push(1);
    }

    rangeWithDots.push(...range);

    if (currentPage + delta < totalPages - 1) {
      rangeWithDots.push('...', totalPages);
    } else if (totalPages > 1) {
      rangeWithDots.push(totalPages);
    }

    return rangeWithDots;
  };

  const visiblePages = getVisiblePages();
  const startItem = (currentPage - 1) * itemsPerPage + 1;
  const endItem = Math.min(currentPage * itemsPerPage, totalItems);

  return (
    <div className="flex flex-col sm:flex-row items-center justify-between gap-4 mt-6">
      {/* Información de items */}
      {showInfo && (
        <div className="text-sm text-textSecondary">
          Mostrando {startItem} - {endItem} de {totalItems} resultados
        </div>
      )}

      {/* Controles de paginación */}
      <div className="flex items-center gap-1">
        {/* Botón anterior */}
        <Button
          variant="ghost"
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage === 1}
          className="p-2"
        >
          <ChevronLeft size={16} />
        </Button>

        {/* Números de página */}
        {visiblePages.map((page, index) => (
          <motion.div
            key={index}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            {page === '...' ? (
              <div className="px-3 py-2 text-textSecondary">
                <MoreHorizontal size={16} />
              </div>
            ) : (
              <Button
                variant={currentPage === page ? 'primary' : 'ghost'}
                onClick={() => onPageChange(page as number)}
                className="min-w-[40px] h-10"
              >
                {page}
              </Button>
            )}
          </motion.div>
        ))}

        {/* Botón siguiente */}
        <Button
          variant="ghost"
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
          className="p-2"
        >
          <ChevronRight size={16} />
        </Button>
      </div>
    </div>
  );
}
