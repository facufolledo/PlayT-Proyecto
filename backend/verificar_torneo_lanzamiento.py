#!/usr/bin/env python3
"""
Script para verificar el torneo de lanzamiento
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database.config import get_db
from src.models.torneo_models import Torneo, TorneoCategoria, TorneoPareja
from sqlalchemy import func

def verificar_torneo():
    """Verificar el torneo de lanzamiento"""
    db = next(get_db())
    
    try:
        # Buscar el último torneo creado
        torneo = db.query(Torneo).order_by(Torneo.id.desc()).first()
        
        if not torneo:
            print("❌ No se encontró ningún torneo")
            return
        
        print(f"🏆 TORNEO: {torneo.nombre}")
        print(f"{'='*60}")
        print(f"📋 ID: {torneo.id}")
        print(f"📅 Fechas: {torneo.fecha_inicio} al {torneo.fecha_fin}")
        print(f"📍 Lugar: {torneo.lugar}")
        print(f"💰 Inscripción: ${torneo.monto_inscripcion}")
        print(f"📊 Estado: {torneo.estado}")
        
        # Obtener categorías
        categorias = db.query(TorneoCategoria).filter(
            TorneoCategoria.torneo_id == torneo.id
        ).all()
        
        print(f"\n📂 CATEGORÍAS ({len(categorias)}):")
        print(f"{'='*60}")
        
        total_parejas = 0
        parejas_sin_restricciones = 0
        parejas_con_restricciones = 0
        
        for cat in categorias:
            # Contar parejas
            parejas = db.query(TorneoPareja).filter(
                TorneoPareja.torneo_id == torneo.id,
                TorneoPareja.categoria_id == cat.id
            ).all()
            
            # Analizar restricciones
            sin_rest = sum(1 for p in parejas if not p.disponibilidad_horaria or len(p.disponibilidad_horaria) == 0)
            con_rest = len(parejas) - sin_rest
            
            total_parejas += len(parejas)
            parejas_sin_restricciones += sin_rest
            parejas_con_restricciones += con_rest
            
            print(f"\n{cat.nombre}:")
            print(f"   👥 Parejas: {len(parejas)}/{cat.max_parejas}")
            print(f"   ✅ Sin restricciones: {sin_rest}")
            print(f"   🚫 Con restricciones: {con_rest}")
            
            # Mostrar ejemplos de restricciones
            if con_rest > 0:
                ejemplos = [p for p in parejas if p.disponibilidad_horaria and len(p.disponibilidad_horaria) > 0][:2]
                for i, pareja in enumerate(ejemplos, 1):
                    rest = pareja.disponibilidad_horaria
                    if len(rest) == 1:
                        r = rest[0]
                        print(f"      Ej{i}: No puede {r['dia']} {r['inicio']}-{r['fin']}")
                    else:
                        print(f"      Ej{i}: {len(rest)} restricciones")
        
        # Resumen general
        print(f"\n📊 RESUMEN GENERAL:")
        print(f"{'='*60}")
        print(f"👥 Total parejas: {total_parejas}")
        print(f"👤 Total jugadores: {total_parejas * 2}")
        print(f"✅ Sin restricciones: {parejas_sin_restricciones} ({parejas_sin_restricciones/total_parejas*100:.1f}%)")
        print(f"🚫 Con restricciones: {parejas_con_restricciones} ({parejas_con_restricciones/total_parejas*100:.1f}%)")
        
        # Horarios del torneo
        print(f"\n⏰ HORARIOS DEL TORNEO:")
        print(f"{'='*60}")
        if torneo.horarios_disponibles:
            for dia, horario in torneo.horarios_disponibles.items():
                print(f"   {dia.capitalize()}: {horario.get('inicio', 'N/A')} - {horario.get('fin', 'N/A')}")
        
        print(f"\n🧪 PRÓXIMOS PASOS PARA PROBAR:")
        print(f"{'='*60}")
        print(f"1. Generar zonas por categoría:")
        print(f"   POST /torneos/{torneo.id}/categorias/{{categoria_id}}/generar-zonas")
        print(f"\n2. Generar fixture global:")
        print(f"   POST /torneos/{torneo.id}/generar-fixture-global")
        print(f"\n3. Ver fixture generado:")
        print(f"   GET /torneos/{torneo.id}/fixture")
        print(f"\n4. Verificar que se respeten restricciones:")
        print(f"   - Ningún partido debe programarse en horarios restringidos")
        print(f"   - Parejas sin restricciones deben tener más flexibilidad")
        
        print(f"\n🔗 ACCESO:")
        print(f"{'='*60}")
        print(f"Frontend: https://drive-plus.com.ar/torneos/{torneo.id}")
        print(f"API: https://drive-plus-production.up.railway.app/torneos/{torneo.id}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    verificar_torneo()
