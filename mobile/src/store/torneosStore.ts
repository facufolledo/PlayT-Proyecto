import { create } from 'zustand';
import { Torneo } from '../types';

interface TorneosState {
  torneos: Torneo[];
  torneoSeleccionado: Torneo | null;
  filtroEstado: 'todos' | 'activos' | 'finalizados';
  loading: boolean;
  
  setTorneos: (torneos: Torneo[]) => void;
  setTorneoSeleccionado: (torneo: Torneo | null) => void;
  setFiltroEstado: (filtro: 'todos' | 'activos' | 'finalizados') => void;
  setLoading: (loading: boolean) => void;
  
  agregarTorneo: (torneo: Torneo) => void;
  actualizarTorneo: (id: number, torneo: Partial<Torneo>) => void;
  eliminarTorneo: (id: number) => void;
}

export const useTorneosStore = create<TorneosState>((set) => ({
  torneos: [],
  torneoSeleccionado: null,
  filtroEstado: 'activos',
  loading: false,

  setTorneos: (torneos) => set({ torneos }),
  setTorneoSeleccionado: (torneo) => set({ torneoSeleccionado: torneo }),
  setFiltroEstado: (filtro) => set({ filtroEstado: filtro }),
  setLoading: (loading) => set({ loading }),

  agregarTorneo: (torneo) => set((state) => ({
    torneos: [torneo, ...state.torneos],
  })),

  actualizarTorneo: (id, torneoActualizado) => set((state) => ({
    torneos: state.torneos.map((t) =>
      t.id === id ? { ...t, ...torneoActualizado } : t
    ),
    torneoSeleccionado:
      state.torneoSeleccionado?.id === id
        ? { ...state.torneoSeleccionado, ...torneoActualizado }
        : state.torneoSeleccionado,
  })),

  eliminarTorneo: (id) => set((state) => ({
    torneos: state.torneos.filter((t) => t.id !== id),
    torneoSeleccionado:
      state.torneoSeleccionado?.id === id ? null : state.torneoSeleccionado,
  })),
}));
