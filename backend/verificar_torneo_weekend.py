#!/usr/bin/env python3
"""
Script para verificar el torneo weekend con horarios
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database.config import get_db
from src.models.torneo_models import Torneo, TorneoCategoria, TorneoPareja
from sqlalchemy import func

def verificar_torneo_weekend():
    """Verificar el torneo weekend"""
    db = next(get_db())
    
    try:
        # Buscar el torneo
        torneo = db.query(Torneo).filter(
            Torneo.nombre.like("%Weekend%")
        ).order_by(Torneo.id.desc()).first()
        
        if not torneo:
            print("❌ No se encontró el torneo weekend")
            return
        
        print(f"\n{'='*60}")
        print(f"🏆 VERIFICACIÓN TORNEO WEEKEND")
        print(f"{'='*60}")
        print(f"ID: {torneo.id}")
        print(f"Nombre: {torneo.nombre}")
        print(f"Fechas: {torneo.fecha_inicio} al {torneo.fecha_fin}")
        print(f"Estado: {torneo.estado}")
        
        # Horarios
        print(f"\n⏰ HORARIOS DISPONIBLES:")
        if torneo.horarios_disponibles:
            for dia, horario in torneo.horarios_disponibles.items():
                print(f"   • {dia.capitalize()}: {horario['inicio']} - {horario['fin']}")
        else:
            print("   ⚠️ Sin horarios configurados")
        
        # Categorías
        categorias = db.query(TorneoCategoria).filter(
            TorneoCategoria.torneo_id == torneo.id
        ).all()
        
        print(f"\n📂 CATEGORÍAS ({len(categorias)}):")
        total_parejas = 0
        for cat in categorias:
            parejas_count = db.query(func.count(TorneoPareja.id)).filter(
                TorneoPareja.categoria_id == cat.id
            ).scalar()
            total_parejas += parejas_count
            print(f"   • {cat.nombre} ({cat.genero}): {parejas_count} parejas")
        
        # Parejas con restricciones
        parejas = db.query(TorneoPareja).filter(
            TorneoPareja.torneo_id == torneo.id
        ).all()
        
        sin_restricciones = 0
        con_restricciones = 0
        restricciones_por_dia = {
            "viernes": 0,
            "sabado": 0,
            "domingo": 0
        }
        
        for pareja in parejas:
            if not pareja.disponibilidad_horaria or len(pareja.disponibilidad_horaria) == 0:
                sin_restricciones += 1
            else:
                con_restricciones += 1
                for restriccion in pareja.disponibilidad_horaria:
                    dia = restriccion.get('dia', '').lower()
                    if dia in restricciones_por_dia:
                        restricciones_por_dia[dia] += 1
        
        print(f"\n👥 PAREJAS ({total_parejas}):")
        print(f"   ✅ Sin restricciones: {sin_restricciones} ({sin_restricciones/total_parejas*100:.1f}%)")
        print(f"   🚫 Con restricciones: {con_restricciones} ({con_restricciones/total_parejas*100:.1f}%)")
        
        print(f"\n🚫 RESTRICCIONES POR DÍA:")
        for dia, count in restricciones_por_dia.items():
            print(f"   • {dia.capitalize()}: {count} parejas")
        
        # Capacidad estimada
        print(f"\n📊 CAPACIDAD ESTIMADA:")
        print(f"   • Viernes: 15:00-23:59 = 9 horas × 3 canchas = 27 horas-cancha")
        print(f"   • Sábado: 09:00-23:59 = 15 horas × 3 canchas = 45 horas-cancha")
        print(f"   • Domingo: 09:00-23:59 = 15 horas × 3 canchas = 45 horas-cancha")
        print(f"   • TOTAL: 117 horas-cancha disponibles")
        print(f"   • Partidos estimados (1.5h c/u): ~78 partidos")
        print(f"   • Parejas inscritas: {total_parejas}")
        
        # Calcular partidos necesarios (estimación)
        partidos_necesarios = 0
        for cat in categorias:
            parejas_cat = db.query(func.count(TorneoPareja.id)).filter(
                TorneoPareja.categoria_id == cat.id
            ).scalar()
            # Fase de grupos: cada pareja juega 3-4 partidos
            # Playoffs: ~50% de parejas
            partidos_cat = parejas_cat * 3.5  # Promedio
            partidos_necesarios += partidos_cat
        
        print(f"\n🎯 ANÁLISIS:")
        print(f"   • Partidos necesarios (estimado): ~{int(partidos_necesarios)}")
        print(f"   • Capacidad disponible: ~78 partidos")
        if partidos_necesarios <= 78:
            print(f"   ✅ Capacidad SUFICIENTE")
        else:
            print(f"   ⚠️ Capacidad AJUSTADA (puede requerir optimización)")
        
        print(f"\n🧪 PRÓXIMOS PASOS:")
        print(f"   1. Generar zonas: python -c 'from src.services.torneo_zona_service import TorneoZonaService; TorneoZonaService().generar_zonas_automaticas({torneo.id})'")
        print(f"   2. Generar fixture: Usar endpoint /torneos/{torneo.id}/fixture/generar")
        print(f"   3. Verificar horarios: Revisar que se respeten las restricciones")
        print(f"   4. Verificar canchas: Confirmar distribución en 3 canchas")
        
        print(f"\n{'='*60}")
        print(f"✅ Verificación completada")
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    verificar_torneo_weekend()
